# -*- coding:UTF-8 -*-
import time
import os
import shutil
import platform
sys = platform.system()
import argparse
import logging
from logging import handlers

print("\033[34m[ \033[1;32mNOTE \033[34m] you can enter Num1 Num2: \n\
                      Num1: [ \033[1;31m--tar\033[34m ] tar alarm file\n\
                          n --> no\n\
                          y --> yes\n\
                      Num2: [ \033[1;31m--debug\033[34m ] debug info\n\
                          n --> no\n\
                          y --> yes\033[0m")

# 入参解析
################################
parser = argparse.ArgumentParser(description='Process some integers.') # 首先创建一个ArgumentParser对象
parser.add_argument('--tar', type=str, default="n",
                    help='tar alarm file') # 是否压缩报警
parser.add_argument('--debug', type=str, default="n",
                    help='run in debug') # 是否开启debug模式
args = parser.parse_args()
################################

## 可改动配置项,可根据需求自行修改
#########################################
# 报警文件夹路径
AlarmDirRoot="/data/workspace/result"
LogDir="/data/workspace/IVUSvr/bin/log"
# 输出报警路径，默认当前路径
AlarmOut = os.path.abspath("./")
# 报警类型：
#   0为拷贝两个时间点之间的数据，可跨天设置，作为前端报警反馈用 需要配置下边的 Array_AlarmTime
#   1为拷贝指定报警类型数据，作为固定报警提取用 需要配置下边的 Array_AlarmRule
#   2为拷贝指定报警时间点的数据
AlarmType = 0
# 报警数据类型：
#   0为全部数据拷贝
#   1为只拷贝指定类型 需要配置下边的 AlarmOnly
#   2为除去设置的类型其他的都拷贝 需要配置下边的 AlarmExclude
AlarmDataType = 2

####### 上述配置部分详细配置说明 #########
#AlarmType = 0 的情况下的设置
# 需要拷贝的时间数组，格式为14位数字，前8位是日期,后6位是24小时制时间，比如:20200114160237 指的是2020年1月14号下午4点2分37秒
# 时间数组必须为两个值 分别是拷贝起始时间和终止时间
Array_AlarmTime = [20210407000000, 20210407000200]
#AlarmType=1的情况下需要设置
# 需要拷贝的规则数组，规则之间是并且的关系，比如 "4401000000201" "20200107" "alarm_8" 会把 4401000000201 下边的时间是 20200107 报警类型是 alarm_8 里面文件都拷贝出来
#Array_AlarmRule=["4401000000201", "20200107", "alarm_8"]
#Array_AlarmRule=["20200107", "alarm_8"]
Array_AlarmRule = ["20200107"]

#AlarmType=2的情况下需要设置
# 需要拷贝的时间数组 格式是 yyyy-MM-dd HH:mm:ss
#yyyy：代表年
#M：月份数字。一位数的月份没有前导零
#MM：代表月（MM和M一样，区别就是MM表示从零开始，比如四月份，MM显示04，M显示4，后面的如同）
#dd：代表日
#HH：代表24小时制的小时
#hh：代表12小时制的小时
#mm：代表分钟
#ss：代表秒
#Array_TimeRule = ["2020-11-04 10:11:32","2020-11-04 10:09:42"]
Array_TimeRule = ["2020-10-27 17:27:31"]

## AlarmDataType 是和IVU的报警参数相关，若IVU的报警类型增加，这里也要相应的调整，下边是当前的报警类型定义
# //报警类型
# typedef enum IVU_ALARM
# {
# IVU_ALARM_STOP = 1,                                   // 停驶
# IVU_SLOW_PASS = 2,                                    // 单车慢速经过
# IVU_ALARM_CONVERSE = 4,                               // 逆行
# IVU_ALARM_REVERSE = 8,                                // 倒车
# IVU_ALARM_ACCIDENT = 16,                              // 事故（以多车违停来定义）
# IVU_ALARM_DAY_CONGESTION = 32,                        // 日间拥堵
# IVU_ALARM_NIGHT_CONGESTION = 64,                      // 夜间拥堵
# IVU_ALARM_NON_VEHICLE = 128,                          // 行人、两轮车、三轮车闯入
# IVU_ALARM_ABANDON = 256,                              // 抛洒物
# IVU_ALARM_POWER_OUTAGE = 512,                         // 隧道停电
# IVU_ALARM_RAIN = 1024,                                // 雨
# IVU_ALARM_FROG = 2048,                                // 雾
# IVU_ALARM_SNOW = 4096,                                // 雪
# IVU_ALARM_SMOKE = 8192,                               // 烟
# IVU_DAY_CONGESTION_CLEAR = 16384,                     // 日间拥堵消失
# IVU_NIGHT_CONGESTION_CLEAR = 32768,                   // 夜间拥堵消失
# IVU_MUTIL_SLOW = 65536,                               // 多车缓行
# IVU_MUTIL_SLOW_CLEAR = 131072,                        // 多车缓行消失
# IVU_INDEX_CAMREA_MOVE = 262144,                       // 相机移动
# IVU_CONSTRUCTION_AREA = 524288,                       // 施工区域
# IVU_SLOW_STOP = 1048576,                              // 单车慢速停车
# IVU_SLOW_START = 2097152,                             // 单车慢速启动
# IVU_VEHI_INTO_DRIVING_AREA = 4194304,                 // 非机动车闯入行车区域
# IVU_CARRY_PEOPLE = 8388608,                           // 骑车带人
# IVU_WITHOUT_HELMET = 16777216,                        // 未戴头盔
# IVU_NMVE_CONVERSE = 33554432,                         // 非机动车逆行
# IVU_LEFT_TRUCK = 134217728,                           // 货车占左
# IVU_ALARM_COLLECTION = 268435456,                     // 样本采集
# IVU_TEST_ALARM = 536870912,                           // 报警测试，产生一个假报警
# IVU_THUMBNAIL = 1073741824,                           // 缩略图，当前算法服务不用设定，框架在每路算法启动固定时间后直接产生该报警
# }IVU_ALARM;

#AlarmDataType = 1 的情况下的配置
# 只拷贝的报警数据 当前是类型定义如下
AlarmOnly = [1, 2]

#AlarmDataType = 2 的情况下的配置
# 不需要拷贝的报警数据 当前是类型定义如下
AlarmExclude = [262144, 536870912, 1073741824]
#########################################

# 公用类或者函数
################################
class Logger(object):
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'crit':logging.CRITICAL
    }#日志级别关系映射

    def __init__(self,filename,level='info',when='D',backCount=28,fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)#设置日志格式
        self.logger.setLevel(self.level_relations.get(level))#设置日志级别
        sh = logging.StreamHandler()#往屏幕上输出
        sh.setFormatter(format_str) #设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename,when=when,backupCount=backCount,encoding='utf-8')#往文件里写入#指定间隔时间自动生成文件的处理器
        #实例化TimedRotatingFileHandler
        #interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
        # S 秒
        # M 分
        # H 小时、
        # D 天、
        # W 每星期（interval==0时代表星期一）
        # midnight 每天凌晨
        th.setFormatter(format_str)#设置文件里写入的格式
        self.logger.addHandler(sh) #把对象加到logger里
        self.logger.addHandler(th)

# 获取指定路径下的指定文件类型的名字列表
def get_filename(path, filetype):
    L = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[1] == filetype:
                L.append(os.path.join(root, file))
    return L

def get_AllDirInCurrentPath(current_path):
    all_list = os.listdir(current_path)
    dir_list = []
    for cur_info in all_list:
        # 获取文件的绝对路径
        abspath = os.path.join(current_path, cur_info)
        # 判断是否是文件还是目录需要用绝对路径
        if os.path.isdir(abspath):
            #print("{} is dir!".format(abspath))
            dir_list.append(abspath)
        # if os.path.isfile(abspath):
        #     print("{} is file!".format(abspath))
    return dir_list

def get_SeleteDirInCurrentPath(current_path, options):
    now_dir_list = get_AllDirInCurrentPath(current_path)
    selete_dir_list = []
    for each_dir in now_dir_list:
        basename = os.path.basename(each_dir)
        for option in options:
            if option in basename:
                selete_dir_list.append(each_dir)
    return selete_dir_list

from glob import *
def matchWildcard(rootPath = "", pattern = ""):
    rootPath = os.path.abspath(rootPath)
    results = []
    for root,dirs,files in os.walk(rootPath):
        for match in glob(os.path.join(root, pattern)):
            results.append(match.replace('\\', '/'))
    return results

def main():
    NowTime = time.strftime("%Y%m%d-%H%M%S", time.localtime())
    LOG_File = "IVUSvr-copy.log"
    if os.path.exists(LOG_File):
        os.remove(LOG_File)
    Log_All = Logger(LOG_File, level='debug')
    #Log_All.logger.info("NowTime:{}".format(NowTime))
    alarm_out_dir = os.path.join(AlarmOut, NowTime)
    if not os.path.exists(alarm_out_dir):
        os.makedirs(alarm_out_dir)
    array_time_rule_format=[]
    # 报警类型的判定
    if AlarmType == 0:
        # 报警类型 异常输入的判定
        if Array_AlarmTime:
            if len(Array_AlarmTime) == 2:
                if Array_AlarmTime[0] >= Array_AlarmTime[1]:
                    Log_All.logger.error("[copy by time gap][start:{} >= end:{}]".format(Array_AlarmTime[0],Array_AlarmTime[1]))
                    return
                else:
                    Log_All.logger.info("[copy by time gap][ start:{} ][ end:{} ]".format(Array_AlarmTime[0],Array_AlarmTime[1]))
            else:
                Log_All.logger.error("Array_AlarmTime error")
                return
        else:
            Log_All.logger.error("Array_AlarmTime is null")
            return
    elif AlarmType == 1:
        Log_All.logger.error("AlarmType={} not support".format(AlarmType))
    elif AlarmType == 2:
        if len(Array_TimeRule) > 0:
            for each_time_rule in Array_TimeRule:
                if len(each_time_rule) != len(Array_TimeRule[0]):#yyyy-MM-dd HH:mm:ss的长度
                    Log_All.logger.error("time={} Format error".format(each_time_rule))
                    return
                else:
                    name_time = each_time_rule
                    each_time_rule_format = name_time[0:4]+name_time[5:7]+name_time[8:10]+name_time[11:13]+name_time[14:16]+name_time[17:19]
                    array_time_rule_format.append(int(each_time_rule_format))
        else:
            Log_All.logger.error("TimeRule is empty")
    else:
        Log_All.logger.error("AlarmType={} not support".format(AlarmType))

    # 报警数据类型的判定
    if AlarmDataType == 0:
        Log_All.logger.info("[copy all]")
    elif AlarmDataType == 1:
        Log_All.logger.info("[copy only] config={}".format(AlarmOnly))
    elif AlarmDataType == 2:
        Log_All.logger.info("[copy exclude] config={}".format(AlarmExclude))
    else:
        Log_All.logger.error("[AlarmDataType error]")
        return

    options = ["archive", "alarm"]
    now_dir_list = get_SeleteDirInCurrentPath(AlarmDirRoot, options)
    for AlarmDir in now_dir_list:
        judge_in_file = os.path.isdir(AlarmDir)
        AlarmDir_basename = os.path.basename(AlarmDir)
        if not judge_in_file:
            Log_All.logger.error("[ {} ] {} not exist".format(AlarmDir_basename, AlarmDir))
            return
        file_name_1 = []
        file_name_1_done = []
        file_name_1_json = []
        file_name_1_done = get_filename(AlarmDir, ".done")
        if len(file_name_1_done) == 0:
            if args.debug == "y" or args.debug == "yes":
                Log_All.logger.warning("[ {} ] {} have no *.done file".format(AlarmDir_basename, AlarmDir))
        file_name_1_json = get_filename(AlarmDir, ".json")
        if len(file_name_1_json) == 0:
            if args.debug == "y" or args.debug == "yes":
                Log_All.logger.info("[ {} ] {} have no *.json file".format(AlarmDir_basename, AlarmDir))
        file_name_1 = file_name_1_done + file_name_1_json

        # 根据规则以及当前时间段进行筛选
        file_name_2 = []
        for file_name in file_name_1:
            try:
                if args.debug == "y" or args.debug == "yes":
                    Log_All.logger.info("[ {} ] file_name={}".format(AlarmDir_basename, file_name))
                file_split = file_name.split("/")
                if len(file_split) <= 4:
                    Log_All.logger.warning("[ {} ] {} tree less than 4".format(AlarmDir_basename, file_name))
                    continue
                file_name_only = file_split[-1]
                alalm_type = file_split[-2].split("_")[1]
                alarm_day = file_split[-3]
                device_id = file_split[-4]
                file_time = file_name_only.split(".")[0].split("_")[1]
                if args.debug == "y" or args.debug == "yes":
                    Log_All.logger.info("[ {} ] file_time={}".format(AlarmDir_basename, file_time))
                data_file = os.path.dirname(file_name)
                if args.debug == "y" or args.debug == "yes":
                    Log_All.logger.info("[ {} ] file_time={}, AlarmTime[0]={}, AlarmTime[1]={}".format(AlarmDir_basename, file_time, Array_AlarmTime[0],Array_AlarmTime[1]))
                if AlarmType == 0:
                    if int(file_time) >= Array_AlarmTime[0] and int(file_time) <= Array_AlarmTime[1]:
                        if args.debug == "y" or args.debug == "yes":
                            Log_All.logger.info("[ {} ] file_time={} in time gap=[{} {}]".format(AlarmDir_basename, int(file_time),Array_AlarmTime[0],Array_AlarmTime[1]))
                        if AlarmDataType == 0:
                            file_name_2.append(file_name)
                        if AlarmDataType == 1:
                            if len(AlarmOnly) > 0:
                                if int(alalm_type) in AlarmOnly:
                                    Log_All.logger.info("[ {} ] alalm_type={} in AlarmOnly so copy".format(AlarmDir_basename, int(alalm_type)))
                                    file_name_2.append(file_name)
                                else:
                                    Log_All.logger.info("[ {} ] alalm_type={} not in AlarmOnly so do nothing".format(AlarmDir_basename,
                                        int(alalm_type)))
                            else:
                                Log_All.logger.error("[ {} ] AlarmOnly={} set error".format(AlarmDir_basename, AlarmOnly))
                                return
                        if AlarmDataType == 2:
                            if len(AlarmExclude) > 0:
                                if int(alalm_type) not in  AlarmExclude:
                                    if args.debug == "y" or args.debug == "yes":
                                        Log_All.logger.info("[ {} ] alalm_type={} not in AlarmExclude so copy".format(AlarmDir_basename, int(alalm_type)))
                                    file_name_2.append(file_name)
                                else:
                                    if args.debug == "y" or args.debug == "yes":
                                        Log_All.logger.info("[ {} ] alalm_type={} in AlarmExclude so do nothing".format(AlarmDir_basename, int(alalm_type)))
                            else:
                                Log_All.logger.error("[ {} ] AlarmExclude = {} set error".format(AlarmDir_basename, AlarmExclude))
                                return
                    else:
                        if args.debug == "y" or args.debug == "yes":
                            Log_All.logger.info("[ {} ] file_time={} not in time gap=[{} {}]".format(AlarmDir_basename, int(file_time),Array_AlarmTime[0],Array_AlarmTime[1]))
                elif AlarmType == 1:
                    Log_All.logger.error("[ {} ] AlarmType={} not support".format(AlarmDir_basename, AlarmType))
                elif AlarmType == 2:
                    for each_time_rule_format in array_time_rule_format:
                        if args.debug == "y" or args.debug == "yes":
                            Log_All.logger.info("[ {} ] file_time={} each_time_rule_format={}".format(AlarmDir_basename, int(file_time),each_time_rule_format))
                        if int(file_time) == each_time_rule_format:
                            file_name_2.append(file_name)
                            break
                else:
                    Log_All.logger.error("[ {} ] AlarmType={} not support".format(AlarmDir_basename, AlarmType))
            except:
                Log_All.logger.error("[ {} ] file_name={} error".format(AlarmDir_basename, file_name))
                continue
        #Log_All.logger.info("[ {} ] all file num={}".format(AlarmDir_basename, len(file_name_2)))
        for i in range(len(file_name_2)):
            file_name = file_name_2[i]
            if args.debug == "y" or args.debug == "yes":
                Log_All.logger.info("[ {} ] file_name={}".format(AlarmDir_basename, file_name))
            file_name_only = os.path.basename(file_name)
            temp_array = file_name_only.split("_")
            if len(temp_array) >= 3:
                file_short = "_".join(temp_array[0:2])
            else:
                Log_All.logger.error("[ {} ] file={} name error".format(AlarmDir_basename, file_name))
                continue
            source_dir = os.path.dirname(file_name)
            target_dir = source_dir.replace(AlarmDir, alarm_out_dir, 1)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            if args.debug == "y" or args.debug == "yes":
                command = "cp -rvf " + os.path.join(source_dir, file_short) + "* " + target_dir
                Log_All.logger.info("[ {} ] command={}".format(AlarmDir_basename, command))
            else:
                command = "cp -rf " + os.path.join(source_dir, file_short) + "* " + target_dir
            os.system(command)
            if len(file_name_2) != 0:
                Log_All.logger.info("[ {} ][\033[34m 所有: \033[1;32m{} \033[34m | 当前: \033[1;32m{} \033[34m | 进度: \033[1;32m{}% \033[34m\033[0m]".format(AlarmDir_basename, len(file_name_2), i+1, int((i+1)*100/len(file_name_2))))
    # 拷贝log
    log_file_name = matchWildcard(LogDir, "INFO*")
    log_file_name.sort()
    log_file_name2 = []
    if len(log_file_name) >= 1:
        for i in range(0, len(log_file_name)-1):
            file_name = log_file_name[i+1]
            strs = os.path.split(file_name)
            if len(strs) > 0:
                file_name_base = strs[-1]
                file_time = file_name_base[5:13] + "000000"
                if int(file_time) > Array_AlarmTime[0]:
                    log_file_name2.append(log_file_name[i])
                    break
            else:
                continue
        if len(log_file_name2) == 0:
            log_file_name2.append(log_file_name[-1])
        for file_name in log_file_name:
            strs = os.path.split(file_name)
            if len(strs) > 0:
                file_name_base = strs[-1]
                file_time = file_name_base[5:13] + "000000"
                if int(file_time) >= Array_AlarmTime[0] and int(file_time) <= Array_AlarmTime[1]:
                    log_file_name2.append(file_name)
            else:
                continue
        data_file_out = os.path.join(AlarmOut, NowTime, "log")
        if not os.path.exists(data_file_out):
            os.makedirs(data_file_out)
        for file_name in log_file_name2:
            command = "cp -rf " + file_name + "* " + data_file_out
            #print('command={}'.format(command))
            os.system(command)
        with open(os.path.join(data_file_out, "time"), 'w') as fp:
            fp.write("start time: {:d}\n".format(Array_AlarmTime[0]))
            fp.write("end time: {:d}\n".format(Array_AlarmTime[1]))

    #拷贝版本升级操作信息
    data_file_out = os.path.join(AlarmOut, NowTime, "log")
    if not os.path.exists(data_file_out):
        os.makedirs(data_file_out)
    command = "cp -rf /data/workspace/Common/server/*.cfg " + data_file_out
    os.system(command)
    #打包数据
    if args.tar == "y" or args.tar == "yes":
        Log_All.logger.info("[ {} ] tar \033[1;32m{}.tar.gz\033[0m begin...".format(AlarmDirRoot, NowTime))
        if os.path.exists(alarm_out_dir):
            if os.listdir(alarm_out_dir):
                if args.debug == "y" or args.debug == "yes":
                    command = "tar -czvPf " + NowTime + ".tar.gz " + alarm_out_dir
                else:
                    command = "tar -czPf " + NowTime + ".tar.gz " + alarm_out_dir
                os.system(command)
                command = "rm -rf " + alarm_out_dir
                os.system(command)
        Log_All.logger.info("[ {} ] tar \033[1;32m{}.tar.gz\033[0m end.".format(AlarmDirRoot, NowTime))
        Log_All.logger.info("报警保存到 \033[1;32m{}.tar.gz\033[0m 发送完 \033[1;31m请删除！！！\033[0m".format(os.path.join(AlarmOut, NowTime)))
    else:
        Log_All.logger.info("报警保存到 \033[1;32m {}\033[0m 发送完 \033[1;31m请删除！！！\033[0m".format(alarm_out_dir))

if __name__ == '__main__':
    main()