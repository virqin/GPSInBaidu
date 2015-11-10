# !/usr/bin python
#--*-- coding:utf-8 --*--
import os
import sys
import re

def get_info(line, reg):
    v = re.findall(reg, line)
    if len(v) > 0:
        #print v[0]
        return 1
    else:
        return 0


file = open("slptt_1.log")


if __name__ == "__main__":

    url = '[2015/11/6 16:38:58.176]	b 114.453109 38.025795 1130834353 4 11 12 63 582 0 0 1 0 13 0 0 0 0 0 0'
    #url = '[2015/11/6 16:35:42.783]	network_ppp_start_cb delay ms=2000'

    v = re.findall('\tb\ (.*?)', url)
    if len(v) == 0:
        print 'non'
    else:
        #l = url.split(' ')
        #l = l[2:]
        print v[0]

    main_hdr = 'date,time,lat,lon,time_stamp,loc_uncertainty_ang,loc_uncertainty_a,loc_uncertainty_p,opt_field_mask,altitude,heading,velocity_hor,fix_type,velocity_ver,loc_uncertainty_v,time_stamp_msec,positioning_source,position_type,gpsUtcOffset,loc_uncertainty_conf,position_mode\n'
    ex_hdr = 'date,time,lat,lon,alongAxisUnc,perpAxisUnc,velHor,velVert,timestamp_tow_ms,timestamp_gps_week,velUncHoriz,velUncVert,pos_reported_to_network\n'
    main_hdr_flag = 0
    ex_hdr_flag = 0
    points = []
    repeat = 0
    while 1:
        lines = file.readlines(100000)
        if not lines:
            break
        for line in lines:
            #1 提取信息到CSV文件
            #1.1 将主结构数据保存到本地CSV文件中
            reg = '\tb\ (.*?)'
            ret = get_info(line, reg) # do something
            if ret == 1:
                # 提取经纬度
                l = line.split(' ')
                l = l[2:4]
                if len(l) > 0:
                    if len(points) > 1:
                        if (points[len(points)-1] == l):
                            repeat = 1
                        else:
                            repeat = 0

                    if repeat != 1:
                        points.append(l)

                l = line.replace('b ','')
                l = l.replace(' ',',')
                l = l.replace('\t',',')
                l = l.replace('[','')
                l = l.replace(']','')
                with open('out_main.csv', 'a') as fp:
                    if main_hdr_flag == 0:
                        fp.writelines(main_hdr)
                        main_hdr_flag = 1
                    fp.writelines(l)

            #1.2 将扩展结构数据保存到本地CSV文件中
            reg = '\te\ (.*?)'
            ret = get_info(line, reg) # do something
            if ret == 1:
                l = line.replace('e ','')
                l = l.replace(' ',',')
                l = l.replace('\t',',')
                l = l.replace('[','')
                l = l.replace(']','')
                with open('out_ex.csv', 'a') as fp:

                    if ex_hdr_flag == 0:
                        fp.writelines(ex_hdr)
                        ex_hdr_flag = 1
                    fp.writelines(l)

    #2 根据记录的经纬度信息生成js数据文件，用于地图显示，格式:
    #var data = {"data":[list],"total":5365,"rt_loc_cnt":47764510,"errorno":0,"NearestTime":"2014-08-29 15:20:00","userTime":"2014-08-29 15:32:11"}
    header = 'var data = {\"data\":['
    content = header
    for p in points:
        data = '[' + p[0] + ', ' + p[1] + ']'
        content = content + data + ','
    content = content + '],\"total\": ' + str(len(points)) + '}'

    with open('points-test-data.js', 'w') as fp:
        fp.write(content)


    #3 根据记录的经纬度信息生成kml数据文件，用于谷歌地球显示:
    from lxml import etree  #将KML节点输出为字符串
    import xlrd             #操作Excel
    from pykml.factory import KML_ElementMaker as KML #使用factory模块

    #使用第一个点创建Folder
    fold = KML.Folder(KML.Placemark(
        KML.Point(KML.coordinates(str(points[0][0]) +','+ str(points[0][1]) +',0'))
        )
    )

    #将剩余的点追加到Folder中
    for i in range(1,len(points)):
        fold.append(KML.Placemark(
        KML.Point(KML.coordinates(str(points[i][0]) +','+ str(points[i][1]) +',0')))
        )

    #使用etree将KML节点输出为字符串数据
    content = etree.tostring(etree.ElementTree(fold),pretty_print=True)

    #保存到文件，然后就可以在Google地球中打开了
    with open('google.kml', 'w') as fp:
        fp.write(content)

