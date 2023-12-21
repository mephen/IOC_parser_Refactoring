from pickle import FALSE
from generator.config import config 
from generator import globals as gr
#import generator.generators as gr
global config

#include header
def generate_include_sentence():
    gr.printFile("#include \"Ioc.h\"")
    gr.printFile("#include \"os.h\"")
    gr.printFile("#include \"system.h\"")
    gr.printFile("#include \"application_Cfg.h\"")
    gr.printFile("#include \"lock.h\"")
    gr.printFile("#include \"os_Cfg.h\"")
    gr.printFile("#include \"core.h\"")
    gr.printFile("#include \"task_Cfg.h\"")
    gr.printFile("#include \"task.h\"")
    gr.printFile("#include \"scheduler.h\"")
    gr.printFile("#include \"ISRInit.h\"")
    gr.printFile("")

#memory copy function
def generate_memcpy_fn():
    gr.printFile("void memcpy_j(int id, void *data, int n, int flag)")
    gr.printFile("{")
    gr.printFile("    IOCCB *cb = &icb[id];")
    gr.printFile("    char *src = (char *)data;")
    gr.printFile("    switch (flag)")
    gr.printFile("    {")
    gr.printFile("    case PUSH:")
    gr.printFile("        for (int i = 0; i < n; i++)")
    gr.printFile("        {")
    gr.printFile("            cb->buffer[cb->tail] = *src;")
    gr.printFile("            cb->tail = (cb->tail + 1) % cb->length;")
    gr.printFile("            src = src + 1;")
    gr.printFile("        }")
    gr.printFile("        break;")
    gr.printFile("    case POP:")
    gr.printFile("        for (int i = 0; i < n; i++)")
    gr.printFile("        {")
    gr.printFile("            *src = cb->buffer[cb->head];")
    gr.printFile("            cb->head = (cb->head + 1) % cb->length;")
    gr.printFile("            src = src + 1;")
    gr.printFile("        }")
    gr.printFile("        break;")
    gr.printFile("    default:")
    gr.printFile("        break;")
    gr.printFile("    }")
    gr.printFile("}\n")

#system call of OS to call IOC
def generate_system_call(ioc, iocids):
    gr.printFile("Std_ReturnType IOC_API(int id, void *input_data, int flag)")
    gr.printFile("{")
    gr.printFile("    switch (id)")
    gr.printFile("    {")

    for iocid in iocids:
        iocDataProperties = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocDataProperties")
        iocsenders = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocSenderProperties")
        iocreceivers = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocReceiverProperties")
        
        gr.printFile("    case {}:".format(iocid))
        gr.printFile("    {")
        gr.printFile("        struct IOC_{}_struct *d = (struct IOC_{}_struct *)input_data;".format(iocid, iocid))    
        
        length = config.getValue("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocBufferLength")
        # send/receive related (buffer length > 0)
        if length != False:
            # sendGroup/receiveGroup
            if len(iocDataProperties) > 1:
                send_datatype = ""
                receiver_datatype = ""
                i = 1
                for iocData in iocDataProperties:
                    iocdataType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                    if "*" not in iocdataType: #type data
                        send_datatype += ("d-> data_" + str(i))
                        receiver_datatype += ("d-> data_" + str(i) + "_r")
                    else:
                        if not(iocdataType.endswith("*")): #改動：type ref, uint16 length 情況
                            send_datatype += ("d-> ptr_" + str(i) + ", " + "d->length_" + str(i))
                            receiver_datatype += ("d-> ptr_" + str(i) + ", " + "d->length_" + str(i) + "_r")
                        else: #type ref
                            send_datatype += ("d-> ptr_" + str(i))
                            receiver_datatype += ("d-> ptr_" + str(i))
                    i += 1
                    if iocData != iocDataProperties[-1]:
                        send_datatype += ", "
                        receiver_datatype += ", "
                
                for sender in iocsenders:
                    gr.printFile("        if (flag == IOC_SEND_{}_{})".format(iocid, sender))
                    gr.printFile("        {")
                    gr.printFile("            return SysIocSendGroup_{}_{}({});".format(iocid, sender, send_datatype))
                    gr.printFile("        }")

                
                for receiver in iocreceivers:
                    gr.printFile("        if (flag == IOC_RECEIVER_{}_{})".format(iocid, receiver))
                    gr.printFile("        {")
                    gr.printFile("            return SysIocReceiveGroup_{}_{}({});".format(iocid, receiver, receiver_datatype))
                    gr.printFile("        }")
                gr.printFile("        else if(flag == IOC_EMPTY)")
                gr.printFile("        {")
                gr.printFile("            return SysIocEmptyQueue_{}();".format(iocid))
                gr.printFile("        }")
                gr.printFile("        break;")
                gr.printFile("    }")
            
            # send/receive
            if len(iocDataProperties) == 1:
                send_datatype = ""
                receiver_datatype = ""
                iocDataProperty = config.getValue("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocDataProperties")
                iocdataType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocDataProperty ,"OsIocDataTypeRef")          
                if "*" not in iocdataType:
                    send_datatype = "d-> data_1"
                    receiver_datatype = "d-> data_1_r"
                else:
                    if not(iocdataType.endswith("*")): #改動：type ref, uint16 length 情況
                        send_datatype += ("d-> ptr_1, d->length_1")
                        receiver_datatype += ("d-> ptr_1, d->length_1_r")
                    else: #type ref
                        send_datatype += ("d-> ptr_1")
                        receiver_datatype += ("d-> ptr_1")
                for sender in iocsenders:
                    gr.printFile("        if (flag == IOC_SEND_{}_{})".format(iocid, sender))
                    gr.printFile("        {")
                    gr.printFile("            return SysIocSend_{}_{}({});".format(iocid, sender, send_datatype))
                    gr.printFile("        }")
                
                for receiver in iocreceivers:
                    gr.printFile("        if (flag == IOC_RECEIVER_{}_{})".format(iocid, receiver))
                    gr.printFile("        {")
                    gr.printFile("            return SysIocReceive_{}({});".format(iocid, receiver_datatype)) ##改動：拿掉 receiver 名稱
                    gr.printFile("        }")
                

                gr.printFile("        else if(flag == IOC_EMPTY)")
                gr.printFile("        {")
                gr.printFile("            return SysIocEmptyQueue_{}();".format(iocid))
                gr.printFile("        }")
                gr.printFile("        break;")
                gr.printFile("    }")    
        # write/read
        else:
            # writeGroup/readGroup
            if len(iocDataProperties) > 1:
                send_datatype = ""
                receiver_datatype = ""
                i = 1
                for iocData in iocDataProperties:
                    iocdataType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                    if "*" not in iocdataType:
                        send_datatype += ("d-> data_" + str(i))
                        receiver_datatype += ("d-> data_" + str(i) + "_r")
                        
                    else:
                        if not(iocdataType.endswith("*")): #改動：type ref, uint16 length 情況
                            send_datatype += ("d-> ptr_" + str(i) + ", " + "d->length_" + str(i))
                            receiver_datatype += ("d-> ptr_" + str(i) + ", " + "d->length_" + str(i) + "_r")
                        else:
                            send_datatype += ("d-> ptr_" + str(i))
                            receiver_datatype += ("d-> ptr_" + str(i))
                    i += 1
                    if iocData != iocDataProperties[-1]:
                        send_datatype += ", "
                        receiver_datatype += ", "
                    
                for sender in iocsenders:
                    gr.printFile("        if (flag == IOC_SEND_{}_{})".format(iocid, sender))
                    gr.printFile("        {")
                    gr.printFile("            return SysIocWriteGroup_{}_{}({});".format(iocid, sender, send_datatype))
                    gr.printFile("        }")

            
                for receiver in iocreceivers:
                    gr.printFile("        if (flag == IOC_RECEIVER_{}_{})".format(iocid, receiver))
                    gr.printFile("        {")
                    gr.printFile("            return SysIocReadGroup_{}_{}({});".format(iocid, receiver, receiver_datatype))
                    gr.printFile("        }")
                gr.printFile("        break;")
                gr.printFile("    }")

            # write/read
            if len(iocDataProperties) == 1: #bug 要改成有/無 group 的情況。
                send_datatype = ""
                receiver_datatype = ""
                iocDataProperty = config.getValue("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocDataProperties")
                iocdataType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocDataProperty ,"OsIocDataTypeRef")          
                if "*" not in iocdataType:
                    send_datatype = "d-> data_1"
                    receiver_datatype = "d-> data_1_r"
                else:
                    if not(iocdataType.endswith("*")): #改動：type ref, uint16 length 情況
                        send_datatype += ("d-> ptr_1, d->length_1")
                        receiver_datatype += ("d-> ptr_1, d->length_1_r")
                    else: #type ref
                        send_datatype += ("d-> ptr_1")
                        receiver_datatype += ("d-> ptr_1")
                for sender in iocsenders:
                    gr.printFile("        if (flag == IOC_SEND_{}_{})".format(iocid, sender))
                    gr.printFile("        {")
                    gr.printFile("            return SysIocWrite_{}_{}({});".format(iocid, sender, send_datatype))
                    gr.printFile("        }")
        
                for receiver in iocreceivers:
                    gr.printFile("        if (flag == IOC_RECEIVER_{}_{})".format(iocid, receiver))
                    gr.printFile("        {")
                    gr.printFile("            return SysIocRead_{}_{}({});".format(iocid, receiver, receiver_datatype))
                    gr.printFile("        }")
                gr.printFile("        break;")
                gr.printFile("    }")
    gr.printFile("    }")
    gr.printFile("}\n")

def generate_lockBit_and_buffer(ioc, iocids):
    for iocid in iocids:
        gr.printFile("uint16 lock_{} = 0;".format(iocid))
        length = config.getValue("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocBufferLength")
        if length != False:
            gr.printFile("uint8 buffer_{}[{}];".format(iocid, length))
        else:
            #no length >> use default buffer length = 30
            gr.printFile("uint8 buffer_{}[30];".format(iocid))

def generate_callback_fn():
    gr.printFile("// PUSH info to systask")
    gr.printFile("Std_ReturnType SetCallbackfunctionAction(ApplicationType reveiverID, void (*callback)(void))")
    gr.printFile("{")
    gr.printFile("    CoreIdType CoreID = (ApplicationVar[reveiverID].CoreRef);")
    gr.printFile("    if (_CoreID == CoreID)")
    gr.printFile("    {")
    gr.printFile("        SysTaskInformationType info;")
    gr.printFile("        info.ApplID = reveiverID;")
    gr.printFile("        info.FunctionPointer = callback;")
    gr.printFile("        info.SysTaskAction = IOCCALLBACK;")
    gr.printFile("        EnSysTaskActionQueue(info);")
    gr.printFile("        ActivateTaskInternal(SysTaskID[_CoreID]);")
    gr.printFile("        ScheduleKernel();")
    gr.printFile("    }")
    gr.printFile("    else")
    gr.printFile("    {")
    gr.printFile("        enableCrossCoreISR();")
    gr.printFile("        GetLock(&CoreParaLock[CoreID], lock_bit);")
    gr.printFile("        CrossCoreServicePara[CoreID].serviceID = SERVICE_CALLBACKFUNCTION;")
    gr.printFile("        CrossCoreServicePara[CoreID].para1 = reveiverID;")
    gr.printFile("        CrossCoreServicePara[CoreID].para2 = callback;")
    gr.printFile("        // CrossCoreServicePara[reveiverID].App = ExecutingApp[_CoreID];\n")

    gr.printFile("        CoreIntFlag[CoreID] = 1;")
    gr.printFile("        InterruptToCore(CoreID);")
    gr.printFile("        while (CoreIntFlag[CoreID] == 1)")
    gr.printFile("            ;")
    gr.printFile("        ReleaseLock(&CoreParaLock[CoreID], lock_bit);")
    gr.printFile("        disableCrossCoreISR();")
    gr.printFile("    }")
    gr.printFile("}\n\n")

#ReceiverTypes which include appID & callback fn.
def generate_ReceiverType(ioc, iocids):
    for iocid in iocids:
        iocreceivers = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocReceiverProperties")
        gr.printFile("ReceiverType receiver_{}[{}] = {}".format(iocid, len(iocreceivers),"{"))
        for iocReceiver in iocreceivers:
            gr.printFile("    {")
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocReceiver ,"OsIocReceivingOsApplicationRef")
            gr.printFile("        .appID = {},".format(app))
            name = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocReceiver ,"OsIocReceiverPullCB")
            if name != False:    
                gr.printFile("        .callback = callback_{}_{},".format(iocid, name))  
        gr.printFile("    },")
        gr.printFile("};")

#IocAutosarType for Ioc_channel_sender & Ioc_channel_receiver
def generate_IocAutosarType(ioc, iocids):
    gr.printFile("IocAutosarType Ioc_channel_sender[IOCID_COUNT] = {")
    for iocid in iocids:
        iocsenders = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocSenderProperties")
        gr.printFileSpace("    0 ")
        for sender in iocsenders:
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + sender ,"OsIocSendingOsApplicationRef")
            if str(app) == "False":
                app = "FALSE"
            if sender == iocsenders[-1]:
                gr.printFile("| (1 << {}),".format(app))
            else:
                gr.printFileSpace("| (1 << {}) ".format(app))
    gr.printFile("};\n")

    gr.printFile("IocAutosarType Ioc_channel_receiver[IOCID_COUNT] = {")
    for iocid in iocids:
        iocreceivers = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocReceiverProperties")
        gr.printFileSpace("    0 ")
        for receiver in iocreceivers:
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + receiver ,"OsIocReceivingOsApplicationRef")
            if str(app) == "False":
                app = "FALSE"
            if receiver == iocreceivers[-1]:
                gr.printFile("| (1 << {}),".format(app))
            else:
                gr.printFileSpace("| (1 << {}) ".format(app))
    gr.printFile("};\n")

#ioc controll block
def generate_IOCCB(ioc, iocids):
    gr.printFile("IOCCB icb[IOCID_COUNT] = {")
    for iocid in iocids:
        length = config.getValue("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocBufferLength")
        if str(length) == "False":
            length = 30 #wirte/read 給定預設的 buffer length 為 30
        iocreceivers = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocReceiverProperties")
        gr.printFile("    {.head = 0,")
        gr.printFile("     .tail = 0,")
        gr.printFile("     .length = {},".format(length))
        gr.printFile("     .channel_receive_num = {},".format(len(iocreceivers)))
        gr.printFile("     .receiver = receiver_{},".format(iocid))
        for iocReceiver in iocreceivers:
            name = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocReceiver ,"OsIocReceiverPullCB")
            if name != False:
                gr.printFile("     .callbackFlag = 1,")
            else:
                gr.printFile("     .callbackFlag = 0,")
        gr.printFile("     .lostFlag = 0,")
        gr.printFile("     .buffer = buffer_{}{},".format(iocid, "}"))
    gr.printFile("};\n")

#for different ioc_api_generator to inherit common code
class ioc_generator():
    def __init__(self, ioc, iocid, iocsenders_or_iocreceivers, iocDataProperties):
        self.ioc = ioc
        self.iocid = iocid
        self.iocsenders_or_iocreceivers = iocsenders_or_iocreceivers
        self.iocDataProperties = iocDataProperties
    def generate_parameters(self):
        pass
    def generate_ioc_code(self, input_para, Is_pointer, iocType):
        pass
    def generate_Sysioc_code(self, input_para, Is_pointer, iocType, data):
        pass
    def generate_IOC_api(self):
        input_para, Is_pointer, iocType, data = self.generate_parameters()
        self.generate_ioc_code(input_para, Is_pointer, iocType)
        self.generate_Sysioc_code(input_para, Is_pointer, iocType, data)

#inherit from ioc_generator
class IocSend_senderId_generator(ioc_generator):
    def __init__(self, ioc, iocid, iocsenders, iocDataProperties):
        super().__init__(ioc, iocid, iocsenders, iocDataProperties)
    
    def generate_parameters(self):
        ioc = self.ioc
        iocid = self.iocid
        iocDataProperties = self.iocDataProperties
        #sender data type
        input_para = ""
        Is_pointer = False
        iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocDataProperties[0] ,"OsIocDataTypeRef")
        if "*" not in iocType:     
            input_para += (iocType + " data_1")
            data_send = iocType 
        else:
            if not(iocType.endswith("*")): #改動：type ref, uint16 length 情況
                ioctype_ptr = iocType.split(",")            
                input_para += ioctype_ptr[0] + " ptr_1" + ", " + "uint16 length_1"
                data_send = ioctype_ptr[1]
            else: #改動：type ref 情況
                input_para += iocType + " ptr_1"
                structure = iocType.replace("*", "")
                data_send = structure 
            Is_pointer = True
        return input_para, Is_pointer, iocType, data_send
    
    def generate_ioc_code(self, input_para, Is_pointer, iocType):
        ioc = self.ioc
        iocid = self.iocid
        iocsenders = self.iocsenders_or_iocreceivers
        for sender in iocsenders:
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + sender ,"OsIocSendingOsApplicationRef")
            gr.printFile("#define OS_OSAPP_{}_START_SEC_CODE".format(app))
            gr.printFile("#include \"OS_MemMap.h\"")
            
            gr.printFile("Std_ReturnType IocSend_{}_{}({})".format(iocid, sender, input_para))
            gr.printFile("{")
            gr.printFile("    struct IOC_{}_struct d;".format(iocid))
            if Is_pointer: #改動：調整下面6行
                if not(iocType.endswith("*")):
                    ioctype_ptr = iocType.split(",")
                    gr.printFile("    d.ptr_1 = ptr_1;")
                    gr.printFile(f"    d.length_1 = length_1;")
                else:
                    gr.printFile("    d.ptr_1 = ptr_1;")
            else:
                gr.printFile("    d.data_1 = data_1;")

            gr.printFile("    SysServiceParaType para;")
            gr.printFile("    para.serviceID = SERVICE_IOC;")
            gr.printFile("    para.para1 = {}; // ioc channel".format(iocid))
            gr.printFile("    para.para2 = &d; // parameter")   
            gr.printFile("    para.para3 = IOC_SEND_{}_{};".format(iocid, sender))
            gr.printFile("    para.result = IOC_E_OK;\n")

            gr.printFile("    pushStack(&para);")
            gr.printFile("    sysCallSystemService();")
            gr.printFile("    popStack(&para);")
            gr.printFile("    return para.result;")
            gr.printFile("}\n")

    def generate_Sysioc_code(self, input_para, Is_pointer, iocType, data_send):
        ioc = self.ioc
        iocid = self.iocid
        iocsenders = self.iocsenders_or_iocreceivers
        for sender in iocsenders:
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + sender ,"OsIocSendingOsApplicationRef")
            gr.printFile("#define OS_OSAPP_{}_STOP_SEC_CODE".format(app))
            gr.printFile("#include \"OS_MemMap.h\"\n")
        
            gr.printFile("Std_ReturnType SysIocSend_{}_{}({})".format(iocid, sender, input_para))
            gr.printFile("{")
            gr.printFile("    Std_ReturnType ret = IOC_E_OK;\n")
        
            gr.printFile("    if (ret == IOC_E_OK && (~(SystemObjectAutosar[_CoreID]->IocAutosar_s[{}].applicationsMask) & (1 << ExecutingApp[_CoreID])))".format(iocid))
            gr.printFile("    {")
            gr.printFile("        ret = IOC_E_NOK;")
            gr.printFile("    }")
            gr.printFile("    if (ret == IOC_E_OK)")
            gr.printFile("    {")
            gr.printFile("        GetLock(&lock_{}, lock_bit);".format(iocid))
            gr.printFile("        IOCCB *cb = &icb[{}];".format(iocid))
                
            if Is_pointer:
                if not(iocType.endswith("*")): #改動：type ref, uint16 length 情況。
                    ioctype_ptr = iocType.split(", ")
                    gr.printFile("        if (length_1 > cb->length)")
                    gr.printFile("        {")
                    gr.printFile("            ret = IOC_E_LENGTH;")
                    gr.printFile("        }")
                    gr.printFile("        if (ret == IOC_E_OK)")
                    gr.printFile("        {")
                    gr.printFile("            int data_size = length_1 + sizeof(uint16);")
                    gr.printFile("            int remain_size = (cb->head - cb->tail + cb->length - 1) % cb->length;")        
                    gr.printFile("            if (data_size > remain_size)")
                    gr.printFile("            {")
                    gr.printFile("                ret = IOC_E_LOST_DATA;")
                    gr.printFile("                cb->lostFlag = 1;")
                    gr.printFile("            }")
                    gr.printFile("        }")
                    gr.printFile("        if (ret == IOC_E_OK)")
                    gr.printFile("        {")
                    gr.printFile("            memcpy_j({}, &{}_1, sizeof({}_1 ), PUSH);".format(iocid, ioctype_ptr[1], data_send))
                    gr.printFile("            memcpy_j({}, ptr_1, {}_1, PUSH);".format(iocid, ioctype_ptr[1]))
                    gr.printFile("        }")
                    gr.printFile("        if (ret == IOC_E_OK && icb[{}].callbackFlag == 1)".format(iocid))
                    gr.printFile("        {")
                    gr.printFile("            for (int i = 0; i < cb->channel_receive_num; i++)")
                    gr.printFile("            {")
                    gr.printFile("                SetCallbackfunctionAction(cb->receiver[i].appID, cb->receiver[i].callback);")
                    gr.printFile("            }")
                    gr.printFile("        }")
                else: #改動：type ref 情況
                    gr.printFile("        if (ret == IOC_E_OK)")
                    gr.printFile("        {")
                    gr.printFile("            int data_size = sizeof({});".format(data_send))
                    gr.printFile("            int remain_size = (cb->head - cb->tail + cb->length - 1) % cb->length;")        
                    gr.printFile("            if (data_size > remain_size)")
                    gr.printFile("            {")
                    gr.printFile("                ret = IOC_E_LIMIT;")
                    gr.printFile("                cb->lostFlag = 1;")
                    gr.printFile("            }")
                    gr.printFile("        }")
                    gr.printFile("        if (ret == IOC_E_OK)")
                    gr.printFile("        {")
                    gr.printFile("            memcpy_j({}, ptr_1, sizeof({}), PUSH);".format(iocid, data_send))
                    gr.printFile("        }")
                    gr.printFile("        if (ret == IOC_E_OK && icb[{}].callbackFlag == 1)".format(iocid))
                    gr.printFile("        {")
                    gr.printFile("            for (int i = 0; i < cb->channel_receive_num; i++)")
                    gr.printFile("            {")
                    gr.printFile("                SetCallbackfunctionAction(cb->receiver[i].appID, cb->receiver[i].callback);")
                    gr.printFile("            }")
                    gr.printFile("        }")

            else:
                gr.printFile("        int data_size = sizeof({});".format(data_send))
                gr.printFile("        int remain_size = (cb->head - cb->tail + cb->length - 1) % cb->length;")
                gr.printFile("        if (data_size > remain_size)")
                gr.printFile("        {")
                gr.printFile("            ret = IOC_E_LOST_DATA;")
                gr.printFile("        }")
                gr.printFile("        if (ret == IOC_E_OK)")
                gr.printFile("        {")
                gr.printFile("            memcpy_j({}, &data_1, sizeof({}), PUSH);\n".format(iocid, data_send))
                gr.printFile("            if (ret == IOC_E_OK && icb[{}].callbackFlag == 1)".format(iocid))
                gr.printFile("            {")
                gr.printFile("                for (int i = 0; i < cb->channel_receive_num; i++)")
                gr.printFile("                {")
                gr.printFile("                    SetCallbackfunctionAction(cb->receiver[i].appID, cb->receiver[i].callback);")
                gr.printFile("                }")
                gr.printFile("            }")
                gr.printFile("        }")
            gr.printFile("        ReleaseLock(&lock_{}, lock_bit);".format(iocid))
            gr.printFile("    }")
        
        
            gr.printFile("#if (HOOK_ENABLE_ERRORHOOK == ENABLE)\n")
            gr.printFile("    if (ret != E_OK && !(systemFlag & (IN_ERROR_HOOK | IN_OSAPP_ERROR_HOOK | IN_OSAPP_SHUTDOWN_HOOK | IN_OSAPP_STARTUP_HOOK)))")
            gr.printFile("    {")
            gr.printFile("        /* System error hook */")
            gr.printFile("        systemFlag |= IN_ERROR_HOOK;")
            gr.printFile("        ErrorHook(ret);")
            gr.printFile("        systemFlag &= ~IN_ERROR_HOOK;")
            gr.printFile("        /* App error hook */\n")
            gr.printFile("#if (HOOK_ENABLE_OSAPP_ERRORHOOK == ENABLE)")
            gr.printFile("        if (ApplicationVar[ExecutingApp[_CoreID]].AppHookFuncArray.ErrorHookFunc != NULL)")
            gr.printFile("        {")
            gr.printFile("            APPErrorHook(ret);")
            gr.printFile("        }")
            gr.printFile("#endif")
            gr.printFile("    }")
            gr.printFile("#endif")
            gr.printFile("    return ret;")
            gr.printFile("}\n")

#inherit from ioc_generator
class IocReceive_generator(ioc_generator):
    def __init__(self, ioc, iocid, iocreceivers, iocDataProperties):
        super().__init__(ioc, iocid, iocreceivers, iocDataProperties)
    
    def generate_parameters(self):
        ioc = self.ioc
        iocid = self.iocid
        iocDataProperties = self.iocDataProperties
        #receiver data type
        input_para = ""
        Is_pointer = False
        iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocDataProperties[0] ,"OsIocDataTypeRef")
        if "*" not in iocType:     
            input_para += (iocType + " *data_1")
            data_re = iocType 
        else:
            if not(iocType.endswith("*")): #改動：type ref, uint16 length 情況
                ioctype_ptr = iocType.split(",")          
                input_para += ioctype_ptr[0] + " ptr_1" + ", " + "uint16* length_1"
                data_re = ioctype_ptr[1]
            else: #改動：type ref 情況
                input_para += iocType + " ptr_1"
                structure = iocType.replace("*", "")
                data_re = structure 
            Is_pointer = True
        return input_para, Is_pointer, iocType, data_re

    def generate_ioc_code(self, input_para, Is_pointer, iocType):
        ioc = self.ioc
        iocid = self.iocid
        iocreceivers = self.iocsenders_or_iocreceivers
        for receiver in iocreceivers:
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + receiver ,"OsIocReceivingOsApplicationRef")
            gr.printFile("#define OS_OSAPP_{}_START_SEC_CODE".format(app))
            gr.printFile("#include \"OS_MemMap.h\"")
            gr.printFile("Std_ReturnType IocReceive_{}({})".format(iocid, input_para))#改動：拿掉 receiver 名稱
            gr.printFile("{")
            gr.printFile("    struct IOC_{}_struct d;".format(iocid))
            if Is_pointer:
                ioctype_ptr = iocType.split(",")
                if not(iocType.endswith("*")): #type ref, uint16 length
                    gr.printFile("    d.ptr_1 = ptr_1;")
                    gr.printFile(f"    d.length_1_r = length_1;")
                else:
                    gr.printFile("    d.ptr_1 = ptr_1;")
            else:
                gr.printFile("    d.data_1_r = data_1;")

            gr.printFile("    SysServiceParaType para;")
            gr.printFile("    para.serviceID = SERVICE_IOC;")
            gr.printFile("    para.para1 = {}; // ioc channel".format(iocid))
            gr.printFile("    para.para2 = &d; // parameter")   
            gr.printFile("    para.para3 = IOC_RECEIVER_{}_{};".format(iocid, receiver))
            gr.printFile("    para.result = IOC_E_OK;\n")

            gr.printFile("    pushStack(&para);")
            gr.printFile("    sysCallSystemService();")
            gr.printFile("    popStack(&para);")
            gr.printFile("    return para.result;")
            gr.printFile("}\n")
            name = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + receiver ,"OsIocReceiverPullCB")
            gr.printFile("void callback_{}(void)".format(iocid)) #callback 內部不重要，由 user 自定義。
            gr.printFile("{")
            gr.printFile("    PrintText(\"callback sucess\\r\\n\\0\");")
            gr.printFile("}\n")

    def generate_Sysioc_code(self, input_para, Is_pointer, iocType, data_re):
        ioc = self.ioc
        iocid = self.iocid
        iocreceivers = self.iocsenders_or_iocreceivers
        for receiver in iocreceivers:
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + receiver ,"OsIocReceivingOsApplicationRef")
            gr.printFile("#define OS_OSAPP_{}_STOP_SEC_CODE".format(app))
            gr.printFile("#include \"OS_MemMap.h\"")
            gr.printFile("Std_ReturnType SysIocReceive_{}({})".format(iocid, input_para))#改動：拿掉 receiver 名稱
            gr.printFile("{")
            gr.printFile("    Std_ReturnType ret = IOC_E_OK;")
            gr.printFile("    if (ret == IOC_E_OK && (~(SystemObjectAutosar[_CoreID]->IocAutosar_r[{}].applicationsMask) & (1 << ExecutingApp[_CoreID])))".format(iocid))
            gr.printFile("    {")
            gr.printFile("        ret = IOC_E_NOK;")
            gr.printFile("    }")
            gr.printFile("    if (ret == IOC_E_OK)")
            gr.printFile("    {")
            
            if Is_pointer:
                gr.printFile("        GetLock(&lock_{}, 1);".format(iocid))
                gr.printFile("        IOCCB *cb = &icb[{}];".format(iocid))
                gr.printFile("        if (cb->tail == cb->head)")
                gr.printFile("        {")
                gr.printFile("            ret = IOC_E_NO_DATA;")
                gr.printFile("        }")
                gr.printFile("        if (ret == IOC_E_OK)")
                gr.printFile("        {")
                if not(iocType.endswith("*")): #改動：type ref, uint16 length 情況。
                    ioctype_ptr = iocType.split(",")
                    gr.printFile("            memcpy_j({}, length_1, sizeof(uint16), POP);".format(iocid))
                    gr.printFile("            memcpy_j({}, ptr_1, *length_1, POP);".format(iocid))
                else: #改動：type ref 情況
                    gr.printFile("            memcpy_j({}, ptr_1, sizeof({}), POP);".format(iocid, data_re))
                gr.printFile("            if (cb->lostFlag == 1)")
                gr.printFile("            {")
                gr.printFile("                cb->lostFlag = 0;")
                gr.printFile("                ret = IOC_E_LOST_DATA;")
                gr.printFile("            }")
                gr.printFile("        }")
                gr.printFile("        ReleaseLock(&lock_{}, 1);".format(iocid))
                gr.printFile("    }") 

            else:
                gr.printFile("        GetLock(&lock_{}, lock_bit);".format(iocid))
                gr.printFile("        IOCCB *cb = &icb[{}];".format(iocid))
                gr.printFile("        int data_size = sizeof({});".format(data_re))
                gr.printFile("        int stored_size = (cb->tail - cb->head + cb->length) % cb->length;")
                gr.printFile("        if (data_size > stored_size)")
                gr.printFile("        {")
                gr.printFile("            ret = IOC_E_LOST_DATA;")
                gr.printFile("        }")
                gr.printFile("        if (ret == IOC_E_OK)")
                gr.printFile("        {")
                gr.printFile("            memcpy_j({}, data_1, sizeof({}), POP);".format(iocid, data_re))
                gr.printFile("            if (cb->lostFlag == 1)")
                gr.printFile("            {")
                gr.printFile("                cb->lostFlag = 0;")
                gr.printFile("                ret = IOC_E_LOST_DATA;")    
                gr.printFile("            }")
                gr.printFile("        }")
                gr.printFile("        ReleaseLock(&lock_{}, lock_bit);".format(iocid))
                gr.printFile("    }")     


            gr.printFile("#if (HOOK_ENABLE_ERRORHOOK == ENABLE)\n")

            gr.printFile("    if (ret != E_OK && !(systemFlag & (IN_ERROR_HOOK | IN_OSAPP_ERROR_HOOK | IN_OSAPP_SHUTDOWN_HOOK | IN_OSAPP_STARTUP_HOOK)))")
            gr.printFile("    {")
            gr.printFile("        /* System error hook */")
            gr.printFile("        systemFlag |= IN_ERROR_HOOK;")
            gr.printFile("        ErrorHook(ret);")
            gr.printFile("        systemFlag &= ~IN_ERROR_HOOK;")
            gr.printFile("        /* App error hook */\n")

            gr.printFile("#if (HOOK_ENABLE_OSAPP_ERRORHOOK == ENABLE)")
            gr.printFile("        if (ApplicationVar[ExecutingApp[_CoreID]].AppHookFuncArray.ErrorHookFunc != NULL)")
            gr.printFile("        {")
            gr.printFile("            APPErrorHook(ret);")
            gr.printFile("        }")
            gr.printFile("#endif")
            gr.printFile("    }")
            gr.printFile("#endif")
            gr.printFile("    return ret;")
            gr.printFile("}\n")        
            
            #empty
            gr.printFile("Std_ReturnType IocEmptyQueue_{}()".format(iocid))
            gr.printFile("{")
            gr.printFile("    SysServiceParaType para;")
            gr.printFile("    para.serviceID = SERVICE_IOC;")
            gr.printFile("    para.para1 = {};        // ioc channel".format(iocid))
            gr.printFile("    para.para2 = NULL;      // parameter")
            gr.printFile("    para.para3 = IOC_EMPTY; // flag 0: send / 1: receive")
            gr.printFile("    para.result = IOC_E_OK;\n")

            gr.printFile("    pushStack(&para);")
            gr.printFile("    sysCallSystemService();")
            gr.printFile("    popStack(&para);")
            gr.printFile("    return para.result;")
            gr.printFile("}\n")

            gr.printFile("Std_ReturnType SysIocEmptyQueue_{}(void)".format(iocid))
            gr.printFile("{")
            gr.printFile("    Std_ReturnType ret = IOC_E_OK;")
            gr.printFile("    // how to get appID")
            gr.printFile("    if (ret == IOC_E_OK && (~(SystemObjectAutosar[_CoreID]->IocAutosar_r[{}].applicationsMask) & (1 << ExecutingApp[_CoreID])))".format(iocid))
            gr.printFile("    {")
            gr.printFile("        ret = IOC_E_NOK;")
            gr.printFile("    }")
            gr.printFile("    if (ret == E_OK)")
            gr.printFile("    {")
            gr.printFile("        GetLock(&lock_{}, 1);".format(iocid))
            gr.printFile("        IOCCB *cb = &icb[{}];".format(iocid))
            gr.printFile("        cb->head = cb->tail = 0;")
            gr.printFile("        ReleaseLock(&lock_{}, 1);".format(iocid))
            gr.printFile("    }")
            gr.printFile("#if (HOOK_ENABLE_ERRORHOOK == ENABLE)\n")

            gr.printFile("    if (ret != E_OK && !(systemFlag & (IN_ERROR_HOOK | IN_OSAPP_ERROR_HOOK | IN_OSAPP_SHUTDOWN_HOOK | IN_OSAPP_STARTUP_HOOK)))")
            gr.printFile("    {")
            gr.printFile("        /* System error hook */")
            gr.printFile("        systemFlag |= IN_ERROR_HOOK;")
            gr.printFile("        ErrorHook(ret);")
            gr.printFile("        systemFlag &= ~IN_ERROR_HOOK;")
            gr.printFile("        /* App error hook */")

            gr.printFile("#if (HOOK_ENABLE_OSAPP_ERRORHOOK == ENABLE)")
            gr.printFile("        if (ApplicationVar[ExecutingApp[_CoreID]].AppHookFuncArray.ErrorHookFunc != NULL)")
            gr.printFile("        {")
            gr.printFile("            APPErrorHook(ret);")
            gr.printFile("        }")
            gr.printFile("#endif")
            gr.printFile("    }")
            gr.printFile("#endif")
            gr.printFile("    return ret;")
            gr.printFile("}")

#inherit from ioc_generator
class IocSendGroup_generator(ioc_generator):
    def __init__(self, ioc, iocid, iocsenders, iocDataProperties):
        super().__init__(ioc, iocid, iocsenders, iocDataProperties)
        self.length_index = []

    def generate_parameters(self):
        ioc = self.ioc
        iocid = self.iocid
        iocDataProperties = self.iocDataProperties
        #sender data type
        i = 1
        input_para = ""
        Is_pointer = False
        self.length_index = []
        for iocData in iocDataProperties:
            iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
            if "*" not in iocType:     
                input_para += (iocType + " data_" + str(i))
            else:
                if not(iocType.endswith("*")): #改動：type ref, uint16 length 情況
                    ioctype_ptr = iocType.split(",")            
                    input_para += ioctype_ptr[0] + " ptr_" + str(i) + ", "  + "uint16 length_" + str(i)
                    self.length_index.append(str(i))
                else: #改動：type ref 情況
                    input_para += iocType + " ptr_" + str(i)
                Is_pointer = True
            if iocData != iocDataProperties[-1]:
                input_para += ", "
            i += 1
        return input_para, Is_pointer, iocType, None
    
    def generate_ioc_code(self, input_para, Is_pointer, iocType):
        ioc = self.ioc
        iocid = self.iocid
        iocsenders = self.iocsenders_or_iocreceivers
        iocDataProperties = self.iocDataProperties
        for sender in iocsenders:
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + sender ,"OsIocSendingOsApplicationRef")
            gr.printFile("#define OS_OSAPP_{}_START_SEC_CODE".format(app))
            gr.printFile("#include \"OS_MemMap.h\"")
            
            gr.printFile("Std_ReturnType IocSendGroup_{}_{}({})".format(iocid, sender, input_para))
            gr.printFile("{")
            gr.printFile("    struct IOC_{}_struct d;".format(iocid))
            j = 1
            for iocData in iocDataProperties:
                iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                if "*" not in iocType:     
                    gr.printFile("    d.data_{} = data_{};".format(j, j))
                else:
                    if not(iocType.endswith("*")): #改動：type ref, uint16 length 情況
                        ioctype_ptr = iocType.split(",")
                        gr.printFile("    d.ptr_{} = ptr_{};".format(j, j))
                        gr.printFile("    d.length_{} = length_{};".format(j, j))
                    else: #改動：type ref 情況
                        gr.printFile("    d.ptr_{} = ptr_{};".format(j, j))
                j += 1
                
            gr.printFile("    SysServiceParaType para;")
            gr.printFile("    para.serviceID = SERVICE_IOC;")
            gr.printFile("    para.para1 = {}; // ioc channel".format(iocid))
            gr.printFile("    para.para2 = &d; // parameter")   
            gr.printFile("    para.para3 = IOC_SEND_{}_{};".format(iocid, sender))
            gr.printFile("    para.result = IOC_E_OK;\n")

            gr.printFile("    pushStack(&para);")
            gr.printFile("    sysCallSystemService();")
            gr.printFile("    popStack(&para);")
            gr.printFile("    return para.result;")
            gr.printFile("}\n")
    
    def generate_Sysioc_code(self, input_para, Is_pointer, iocType, data_send):
        ioc = self.ioc
        iocid = self.iocid
        iocsenders = self.iocsenders_or_iocreceivers
        iocDataProperties = self.iocDataProperties
        for sender in iocsenders:
            length_index = self.length_index
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + sender ,"OsIocSendingOsApplicationRef")
            gr.printFile("#define OS_OSAPP_{}_STOP_SEC_CODE".format(app))
            gr.printFile("#include \"OS_MemMap.h\"\n")
        
            gr.printFile("Std_ReturnType SysIocSendGroup_{}_{}({})".format(iocid, sender, input_para))
            gr.printFile("{")
            gr.printFile("    Std_ReturnType ret = IOC_E_OK;\n")
        
            gr.printFile("    if (ret == IOC_E_OK && (~(SystemObjectAutosar[_CoreID]->IocAutosar_s[{}].applicationsMask) & (1 << ExecutingApp[_CoreID])))".format(iocid))
            gr.printFile("    {")
            gr.printFile("        ret = IOC_E_NOK;")
            gr.printFile("    }")
            gr.printFile("    if (ret == IOC_E_OK)")
            gr.printFile("    {")
            gr.printFile("        GetLock(&lock_{}, lock_bit);".format(iocid))
            gr.printFile("        IOCCB *cb = &icb[{}];".format(iocid))   
            if "length" in input_para:
                gr.printFileSpace("        int length = ")       
                for index in length_index:
                    gr.printFileSpace(f"length_{index}")
                    if index != length_index[-1]:
                        gr.printFileSpace(" + ")
                gr.printFile(";")
                gr.printFile("        if (length == 0 || length > cb->length)")
                gr.printFile("        {")
                gr.printFile("            ret = IOC_E_LENGTH;")
                gr.printFile("        }")
            gr.printFile("        if (ret == IOC_E_OK)")
            gr.printFile("        {")
            gr.printFileSpace("            int data_size = ")
            j = 1
            for iocData in iocDataProperties:
                iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                if "*" not in iocType:     
                    gr.printFileSpace("sizeof({})".format(iocType)) 
                else:
                    if not(iocType.endswith("*")): #改動：type ref, uint16 length 情況
                        ioctype_ptr = iocType.split(",")
                        gr.printFileSpace("length_{} + sizeof(uint16)".format(str(j)))
                    else:
                        gr.printFileSpace("sizeof({})".format(iocType.replace("*", "")))
                j += 1

                if iocData != iocDataProperties[-1]:
                    gr.printFileSpace(" + ")
                else:
                    gr.printFileSpace(";\n")

            gr.printFile("            int remain_size = (cb->head - cb->tail + cb->length - 1) % cb->length;")        
            gr.printFile("            if (data_size > remain_size)")
            gr.printFile("            {")
            if "*" in input_para: # (type ref(, uint16 length))
                gr.printFile("                cb->lostFlag = 1;")
                gr.printFile("                ret = IOC_E_LIMIT;")
            else:
                gr.printFile("                ret = IOC_E_LOST_DATA;")
            gr.printFile("            }")
            gr.printFile("        }")
            gr.printFile("        if (ret == IOC_E_OK)")
            gr.printFile("        {")
            
            j = 1
            for iocData in iocDataProperties:
                iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                if "*" not in iocType:     
                    gr.printFile("            memcpy_j({}, &data_{}, sizeof({}), PUSH);".format(iocid, j, iocType))
                else:
                    if not(iocType.endswith("*")): #type ref, uint16 length 
                        ioctype_ptr = iocType.split(",")
                        gr.printFile("            memcpy_j({}, &length_{}, sizeof(uint16), PUSH);".format(iocid, j))
                        gr.printFile("            memcpy_j({}, ptr_{}, length_{}, PUSH);".format(iocid, j , j))
                    else:
                        gr.printFile("            memcpy_j({}, ptr_{}, sizeof({}), PUSH);".format(iocid, j , iocType.replace("*", "")))
                j += 1
            gr.printFile("        }")
            gr.printFile("        if (ret == IOC_E_OK && icb[{}].callbackFlag == 1)".format(iocid))
            gr.printFile("        {")
            gr.printFile("            for (int i = 0; i < cb->channel_receive_num; i++)")
            gr.printFile("            {")
            gr.printFile("                SetCallbackfunctionAction(cb->receiver[i].appID, cb->receiver[i].callback);")
            gr.printFile("            }")
            gr.printFile("        }")
            
            gr.printFile("        ReleaseLock(&lock_{}, lock_bit);".format(iocid))
            gr.printFile("    }")
        
        
            gr.printFile("#if (HOOK_ENABLE_ERRORHOOK == ENABLE)\n")
            gr.printFile("    if (ret != E_OK && !(systemFlag & (IN_ERROR_HOOK | IN_OSAPP_ERROR_HOOK | IN_OSAPP_SHUTDOWN_HOOK | IN_OSAPP_STARTUP_HOOK)))")
            gr.printFile("    {")
            gr.printFile("        /* System error hook */")
            gr.printFile("        systemFlag |= IN_ERROR_HOOK;")
            gr.printFile("        ErrorHook(ret);")
            gr.printFile("        systemFlag &= ~IN_ERROR_HOOK;")
            gr.printFile("        /* App error hook */\n")
            gr.printFile("#if (HOOK_ENABLE_OSAPP_ERRORHOOK == ENABLE)")
            gr.printFile("        if (ApplicationVar[ExecutingApp[_CoreID]].AppHookFuncArray.ErrorHookFunc != NULL)")
            gr.printFile("        {")
            gr.printFile("            APPErrorHook(ret);")
            gr.printFile("        }")
            gr.printFile("#endif")
            gr.printFile("    }")
            gr.printFile("#endif")

            gr.printFile("    return ret;")
            gr.printFile("}\n")

#inherit from ioc_generator
class IocReceiveGroup_generator(ioc_generator):
    def __init__(self, ioc, iocid, iocreceivers, iocDataProperties):
        super().__init__(ioc, iocid, iocreceivers, iocDataProperties)

    def generate_parameters(self):
        ioc = self.ioc
        iocid = self.iocid
        iocDataProperties = self.iocDataProperties
        i = 1
        input_para = ""
        Is_pointer = False
        for iocData in iocDataProperties:
            iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
            if "*" not in iocType:     
                input_para += (iocType + " *data_" + str(i))
            else:
                if not(iocType.endswith("*")): #改動：type ref, uint16 length 情況
                    ioctype_ptr = iocType.split(",")            
                    input_para += ioctype_ptr[0] + " ptr_" + str(i) + ", " + "uint16* length_" + str(i)
                else:
                    input_para += iocType + " ptr_" + str(i)
                Is_pointer = True
            if iocData != iocDataProperties[-1]:
                input_para += ", "
            i += 1
        return input_para, Is_pointer, iocType, None

    def generate_ioc_code(self, input_para, Is_pointer, iocType):
        ioc = self.ioc
        iocid = self.iocid
        iocDataProperties = self.iocDataProperties
        iocreceivers = self.iocsenders_or_iocreceivers
        for receiver in iocreceivers:
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + receiver ,"OsIocReceivingOsApplicationRef")
            gr.printFile("#define OS_OSAPP_{}_START_SEC_CODE".format(app))
            gr.printFile("#include \"OS_MemMap.h\"")
            gr.printFile("Std_ReturnType IocReceiveGroup_{}_{}({})".format(iocid, receiver, input_para))
            gr.printFile("{")
            gr.printFile("    struct IOC_{}_struct d;".format(iocid))
            j = 1
            for iocData in iocDataProperties:
                iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                if "*" not in iocType:     
                    gr.printFile("    d.data_{}_r = data_{};".format(j, j))
                else:
                    if not(iocType.endswith("*")): #改動：type ref, uint16 length 情況
                        ioctype_ptr = iocType.split(",")   
                        gr.printFile("    d.ptr_{} = ptr_{};".format(j, j))            
                        gr.printFile("    d.length_{}_r = length_{};".format(j, j))
                    else:
                        gr.printFile("    d.ptr_{} = ptr_{};".format(j, j))
                j += 1

            gr.printFile("    SysServiceParaType para;")
            gr.printFile("    para.serviceID = SERVICE_IOC;")
            gr.printFile("    para.para1 = {}; // ioc channel".format(iocid))
            gr.printFile("    para.para2 = &d; // parameter")   
            gr.printFile("    para.para3 = IOC_RECEIVER_{}_{};".format(iocid, receiver))
            gr.printFile("    para.result = IOC_E_OK;\n")

            gr.printFile("    pushStack(&para);")
            gr.printFile("    sysCallSystemService();")
            gr.printFile("    popStack(&para);")
            gr.printFile("    return para.result;")
            gr.printFile("}\n")
            name = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + receiver ,"OsIocReceiverPullCB")
            gr.printFile("void callback_{}_{}(void)".format(iocid, name))
            gr.printFile("{")
            gr.printFile("    int data;")
            gr.printFile("    PrintText(\"callback sucess\\r\\n\\0\");")
            gr.printFile("}\n")

    def generate_Sysioc_code(self, input_para, Is_pointer, iocType, data_re):
        ioc = self.ioc
        iocid = self.iocid
        iocDataProperties = self.iocDataProperties
        iocreceivers = self.iocsenders_or_iocreceivers
        for receiver in iocreceivers:
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + receiver ,"OsIocReceivingOsApplicationRef")
            gr.printFile("#define OS_OSAPP_{}_STOP_SEC_CODE".format(app))
            gr.printFile("#include \"OS_MemMap.h\"")
            gr.printFile("Std_ReturnType SysIocReceiveGroup_{}_{}({})".format(iocid, receiver, input_para))
            gr.printFile("{")
            gr.printFile("    Std_ReturnType ret = IOC_E_OK;")
            gr.printFile("    if (ret == IOC_E_OK && (~(SystemObjectAutosar[_CoreID]->IocAutosar_r[{}].applicationsMask) & (1 << ExecutingApp[_CoreID])))".format(iocid))
            gr.printFile("    {")
            gr.printFile("        ret = IOC_E_NOK;")
            gr.printFile("    }")
            gr.printFile("    if (ret == IOC_E_OK)")
            gr.printFile("    {")
            gr.printFile("        GetLock(&lock_{}, lock_bit);".format(iocid))
            gr.printFile("        IOCCB *cb = &icb[{}];".format(iocid))

            if "*" in input_para: #有 type ref 或 type ref, uint16 length 的參數時
                gr.printFile("        if (cb->head == cb->tail)")
            else: #全為 type data 參數
                gr.printFileSpace("        int data_size = ")
                for iocData in iocDataProperties:
                    iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                    gr.printFileSpace("sizeof({})".format(iocType))
                    if iocData != iocDataProperties[-1]:
                        gr.printFileSpace(" + ")
                gr.printFile("        int stored_size = (cb->tail - cb->head + cb->length) % cb->length;")
                gr.printFile("        if (data_size > stored_size)")

            gr.printFile("        {")
            gr.printFile("            ret = IOC_E_NO_DATA;")
            gr.printFile("        }")
            gr.printFile("        if (ret == IOC_E_OK)")
            gr.printFile("        {")
            j = 1
            for iocData in iocDataProperties:
                iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                if "*" not in iocType:     
                    gr.printFile("            memcpy_j({}, data_{}, sizeof({}), POP);".format(iocid, j, iocType))
                else:
                    if not(iocType.endswith("*")): #改動：type ref, uint16 length 情況
                        ioctype_ptr = iocType.split(",")
                        gr.printFile("            memcpy_j({}, length_{}, sizeof(uint16), POP);".format(iocid, j))
                        gr.printFile("            memcpy_j({}, ptr_{}, *length_{}, POP);".format(iocid, j , j))
                    else:
                        gr.printFile("            memcpy_j({}, ptr_{}, sizeof({}), POP);".format(iocid, j , iocType.replace("*", "")))
                j += 1

            gr.printFile("            if (cb->lostFlag == 1)")
            gr.printFile("            {")
            gr.printFile("                cb->lostFlag = 0;")
            gr.printFile("                ret = IOC_E_LOST_DATA;")
            gr.printFile("            }")
            gr.printFile("        }")
            gr.printFile("        ReleaseLock(&lock_{}, lock_bit);".format(iocid))
            gr.printFile("    }") 

            
            gr.printFile("#if (HOOK_ENABLE_ERRORHOOK == ENABLE)\n")
            gr.printFile("    if (ret != E_OK && !(systemFlag & (IN_ERROR_HOOK | IN_OSAPP_ERROR_HOOK | IN_OSAPP_SHUTDOWN_HOOK | IN_OSAPP_STARTUP_HOOK)))")
            gr.printFile("    {")
            gr.printFile("        /* System error hook */")
            gr.printFile("        systemFlag |= IN_ERROR_HOOK;")
            gr.printFile("        ErrorHook(ret);")
            gr.printFile("        systemFlag &= ~IN_ERROR_HOOK;")
            gr.printFile("        /* App error hook */\n")

            gr.printFile("#if (HOOK_ENABLE_OSAPP_ERRORHOOK == ENABLE)")
            gr.printFile("        if (ApplicationVar[ExecutingApp[_CoreID]].AppHookFuncArray.ErrorHookFunc != NULL)")
            gr.printFile("        {")
            gr.printFile("            APPErrorHook(ret);")
            gr.printFile("        }")
            gr.printFile("#endif")
            gr.printFile("    }")
            gr.printFile("#endif")
            gr.printFile("    return ret;")
            gr.printFile("}\n")        
            
            #empty
            gr.printFile("Std_ReturnType IocEmptyQueue_{}()".format(iocid))
            gr.printFile("{")
            gr.printFile("    SysServiceParaType para;")
            gr.printFile("    para.serviceID = SERVICE_IOC;")
            gr.printFile("    para.para1 = {};        // ioc channel".format(iocid))
            gr.printFile("    para.para2 = NULL;      // parameter")
            gr.printFile("    para.para3 = IOC_EMPTY; // flag 0: send / 1: receive")
            gr.printFile("    para.result = IOC_E_OK;\n")

            gr.printFile("    pushStack(&para);")
            gr.printFile("    sysCallSystemService();")
            gr.printFile("    popStack(&para);")
            gr.printFile("    return para.result;")
            gr.printFile("}\n")

            gr.printFile("Std_ReturnType SysIocEmptyQueue_{}(void)".format(iocid))
            gr.printFile("{")
            gr.printFile("    Std_ReturnType ret = IOC_E_OK;")
            gr.printFile("    // how to get appID")
            gr.printFile("    if (ret == IOC_E_OK && (~(SystemObjectAutosar[_CoreID]->IocAutosar_r[{}].applicationsMask) & (1 << ExecutingApp[_CoreID])))".format(iocid))
            gr.printFile("    {")
            gr.printFile("        ret = IOC_E_NOK;")
            gr.printFile("    }")
            gr.printFile("    if (ret == E_OK)")
            gr.printFile("    {")
            gr.printFile("        GetLock(&lock_{}, lock_bit);".format(iocid))
            gr.printFile("        IOCCB *cb = &icb[{}];".format(iocid))
            gr.printFile("        cb->head = cb->tail = 0;")
            gr.printFile("        ReleaseLock(&lock_{}, lock_bit);".format(iocid))
            gr.printFile("    }")
            gr.printFile("#if (HOOK_ENABLE_ERRORHOOK == ENABLE)\n")

            gr.printFile("    if (ret != E_OK && !(systemFlag & (IN_ERROR_HOOK | IN_OSAPP_ERROR_HOOK | IN_OSAPP_SHUTDOWN_HOOK | IN_OSAPP_STARTUP_HOOK)))")
            gr.printFile("    {")
            gr.printFile("        /* System error hook */")
            gr.printFile("        systemFlag |= IN_ERROR_HOOK;")
            gr.printFile("        ErrorHook(ret);")
            gr.printFile("        systemFlag &= ~IN_ERROR_HOOK;")
            gr.printFile("        /* App error hook */")

            gr.printFile("#if (HOOK_ENABLE_OSAPP_ERRORHOOK == ENABLE)")
            gr.printFile("        if (ApplicationVar[ExecutingApp[_CoreID]].AppHookFuncArray.ErrorHookFunc != NULL)")
            gr.printFile("        {")
            gr.printFile("            APPErrorHook(ret);")
            gr.printFile("        }")
            gr.printFile("#endif")
            gr.printFile("    }")
            gr.printFile("#endif")
            gr.printFile("    return ret;")
            gr.printFile("}")

#inherit from ioc_generator
class IocWrite_senderId_generator(ioc_generator):
    def __init__(self, ioc, iocid, iocsenders, iocDataProperties):
        super().__init__(ioc, iocid, iocsenders, iocDataProperties)
    
    def generate_parameters(self):
        ioc = self.ioc
        iocid = self.iocid
        iocDataProperties = self.iocDataProperties
        i = 1
        input_para = ""
        Is_pointer = False
        for iocData in iocDataProperties:
            iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
            if "*" not in iocType:     
                input_para += (iocType + " data_" + str(i))
            else:
                if not(iocType.endswith("*")): #改動：type ref, uint16 length 情況
                    ioctype_ptr = iocType.split(",")            
                    input_para = ioctype_ptr[0] + " ptr_" + str(i) + ", " + "uint16 length_" + str(i) 
                else: #改動：type ref 情況
                    input_para = iocType + " ptr_" + str(i)
                Is_pointer = True
            if iocData != iocDataProperties[-1]:
                input_para += ", "
            i += 1
        return input_para, Is_pointer, iocType, None

    def generate_ioc_code(self, input_para, Is_pointer, iocType):
        ioc = self.ioc
        iocid = self.iocid
        iocDataProperties = self.iocDataProperties
        iocsenders = self.iocsenders_or_iocreceivers
        for sender in iocsenders:
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + sender ,"OsIocSendingOsApplicationRef")
            gr.printFile("#define OS_OSAPP_{}_START_SEC_CODE".format(app))
            gr.printFile("#include \"OS_MemMap.h\"")
            
            gr.printFile("Std_ReturnType IocWrite_{}_{}({})".format(iocid, sender, input_para))
            gr.printFile("{")
            gr.printFile("    struct IOC_{}_struct d;".format(iocid))
            if Is_pointer:
                iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocDataProperties[0] ,"OsIocDataTypeRef")
                if not(iocType.endswith("*")):
                    ioctype_ptr = iocType.split(",")
                    gr.printFile("    d.ptr_1 = ptr_1;")
                    gr.printFile(f"    d.length_1 = length_1;")
                else:
                    gr.printFile("    d.ptr_1 = ptr_1;")
            else:
                gr.printFile("    d.data_1 = data_1;")

            gr.printFile("    SysServiceParaType para;")
            gr.printFile("    para.serviceID = SERVICE_IOC;")
            gr.printFile("    para.para1 = {}; // ioc channel".format(iocid))
            gr.printFile("    para.para2 = &d; // parameter")   
            gr.printFile("    para.para3 = IOC_SEND_{}_{};".format(iocid, sender))
            gr.printFile("    para.result = IOC_E_OK;\n")

            gr.printFile("    pushStack(&para);")
            gr.printFile("    sysCallSystemService();")
            gr.printFile("    popStack(&para);")
            gr.printFile("    return para.result;")
            gr.printFile("}\n")

    def generate_Sysioc_code(self, input_para, Is_pointer, iocType, data_send):
        ioc = self.ioc
        iocid = self.iocid
        iocDataProperties = self.iocDataProperties
        iocsenders = self.iocsenders_or_iocreceivers
        for sender in iocsenders:
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + sender ,"OsIocSendingOsApplicationRef")
            gr.printFile("#define OS_OSAPP_{}_STOP_SEC_CODE".format(app))
            gr.printFile("#include \"OS_MemMap.h\"\n")
        
            gr.printFile("Std_ReturnType SysIocWrite_{}_{}({})".format(iocid, sender, input_para))
            gr.printFile("{")
            gr.printFile("    Std_ReturnType ret = IOC_E_OK;")
            gr.printFile("    if (ret == IOC_E_OK && (~(SystemObjectAutosar[_CoreID]->IocAutosar_s[{}].applicationsMask) & (1 << ExecutingApp[_CoreID])))".format(iocid))
            gr.printFile("    {")
            gr.printFile("        ret = IOC_E_NOK;")
            gr.printFile("    }")
            gr.printFile("    if (ret == IOC_E_OK)")
            gr.printFile("    {")
            gr.printFile("        GetLock(&lock_{}, lock_bit);".format(iocid))
            gr.printFile("        IOCCB *cb = &icb[{}];".format(iocid))
            
            iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocDataProperties[0] ,"OsIocDataTypeRef")
            if "*" not in iocType:     
                data_send = iocType 
            else: #改動下面5行
                if not(iocType.endswith("*")):
                    ioctype_ptr = iocType.split(",")            
                    data_send = ioctype_ptr[1]
                else:
                    structure = iocType.replace("*", "")
                    data_send = structure 
            
            if Is_pointer and not(iocType.endswith("*")):#改動：type ref, uint16 length 情況。
                ioctype_ptr = iocType.split(",")
                gr.printFile("        if (length_1 == 0 || length_1 > cb->length)")
                gr.printFile("        {")
                gr.printFile("            ret = IOC_E_LENGTH;")
                gr.printFile("        }")
                gr.printFile("        if (ret == IOC_E_OK)")
                gr.printFile("        {")
                gr.printFile("            memcpy_j({}, &length_1, sizeof(uint16), PUSH);".format(iocid))
                gr.printFile("            memcpy_j({}, ptr_1, length_1, PUSH);".format(iocid))
                gr.printFile("            cb->tail = cb->head = 0;")
                gr.printFile("            if (cb->callbackFlag == 1)")
                gr.printFile("            {")
                gr.printFile("                for (int i = 0; i < cb->channel_receive_num; i++)")
                gr.printFile("                {")
                gr.printFile("                    SetCallbackfunctionAction(cb->receiver[i].appID, cb->receiver[i].callback);")
                gr.printFile("                }")
                gr.printFile("            }")
                gr.printFile("        }")
            else: #type data 和 type ref 情況。
                gr.printFile("        if (ret == IOC_E_OK)")
                gr.printFile("        {")
                if Is_pointer and (iocType.endswith("*")):
                    gr.printFile("            memcpy_j({}, ptr_1, sizeof({}), PUSH);".format(iocid, data_send))
                else:
                    gr.printFile("            memcpy_j({}, &data_1, sizeof({}), PUSH);\n".format(iocid, data_send))
                gr.printFile("            if (ret == IOC_E_OK && icb[{}].callbackFlag == 1)".format(iocid))
                gr.printFile("            {")
                gr.printFile("                for (int i = 0; i < cb->channel_receive_num; i++)")
                gr.printFile("                {")
                gr.printFile("                    SetCallbackfunctionAction(cb->receiver[i].appID, cb->receiver[i].callback);")
                gr.printFile("                }")
                gr.printFile("            }")
                gr.printFile("        }")
            
            gr.printFile("        ReleaseLock(&lock_{}, lock_bit);".format(iocid))
            gr.printFile("    }")
        
        
            gr.printFile("#if (HOOK_ENABLE_ERRORHOOK == ENABLE)\n")
            gr.printFile("    if (ret != E_OK && !(systemFlag & (IN_ERROR_HOOK | IN_OSAPP_ERROR_HOOK | IN_OSAPP_SHUTDOWN_HOOK | IN_OSAPP_STARTUP_HOOK)))")
            gr.printFile("    {")
            gr.printFile("        /* System error hook */")
            gr.printFile("        systemFlag |= IN_ERROR_HOOK;")
            gr.printFile("        ErrorHook(ret);")
            gr.printFile("        systemFlag &= ~IN_ERROR_HOOK;")
            gr.printFile("        /* App error hook */\n")
            gr.printFile("#if (HOOK_ENABLE_OSAPP_ERRORHOOK == ENABLE)")
            gr.printFile("        if (ApplicationVar[ExecutingApp[_CoreID]].AppHookFuncArray.ErrorHookFunc != NULL)")
            gr.printFile("        {")
            gr.printFile("            APPErrorHook(ret);")
            gr.printFile("        }")
            gr.printFile("#endif")
            gr.printFile("    }")
            gr.printFile("#endif")

            gr.printFile("    return ret;")
            gr.printFile("}\n")

#inherit from ioc_generator
class IocRead_receiverId_generator(ioc_generator):
    def __init__(self, ioc, iocid, iocreceivers, iocDataProperties):
        super().__init__(ioc, iocid, iocreceivers, iocDataProperties)

    def generate_parameters(self):
        ioc = self.ioc
        iocid = self.iocid
        iocDataProperties = self.iocDataProperties
        i = 1
        input_para = ""
        Is_pointer = False
        for iocData in iocDataProperties:
            iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
            if "*" not in iocType:     
                input_para += (iocType + " *data_" + str(i))
            else:
                if not(iocType.endswith("*")): #改動：type ref, uint16 length 情況
                    ioctype_ptr = iocType.split(",")            
                    input_para = ioctype_ptr[0] + " ptr_" + str(i) + ", uint16* length_1"
                else: #改動：type ref 情況
                    input_para = iocType + " ptr_" + str(i)
                Is_pointer = True
            
            if iocData != iocDataProperties[-1]:
                input_para += ", "
            i += 1
        return input_para, Is_pointer, iocType, None

    def generate_ioc_code(self, input_para, Is_pointer, iocType):
        ioc = self.ioc
        iocid = self.iocid
        iocreceivers = self.iocsenders_or_iocreceivers
        iocDataProperties = self.iocDataProperties
        for receiver in iocreceivers:
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + receiver ,"OsIocReceivingOsApplicationRef")
            gr.printFile("#define OS_OSAPP_{}_START_SEC_CODE".format(app))
            gr.printFile("#include \"OS_MemMap.h\"")
            gr.printFile("Std_ReturnType IocRead_{}_{}({})".format(iocid, receiver, input_para))
            gr.printFile("{")
            gr.printFile("    struct IOC_{}_struct d;".format(iocid))
            if Is_pointer:
                iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocDataProperties[0] ,"OsIocDataTypeRef")
                if not(iocType.endswith("*")):
                    ioctype_ptr = iocType.split(",")
                    gr.printFile("    d.ptr_1 = ptr_1;")
                    gr.printFile(f"    d.length_1_r = length_1;")
                else:
                    gr.printFile("    d.ptr_1 = ptr_1;")
            else:
                gr.printFile("    d.data_1_r = data_1;")

            gr.printFile("    SysServiceParaType para;")
            gr.printFile("    para.serviceID = SERVICE_IOC;")
            gr.printFile("    para.para1 = {}; // ioc channel".format(iocid))
            gr.printFile("    para.para2 = &d; // parameter")   
            gr.printFile("    para.para3 = IOC_RECEIVER_{}_{};".format(iocid, receiver))
            gr.printFile("    para.result = IOC_E_OK;\n")

            gr.printFile("    pushStack(&para);")
            gr.printFile("    sysCallSystemService();")
            gr.printFile("    popStack(&para);")
            gr.printFile("    return para.result;")
            gr.printFile("}\n")

            name = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + receiver ,"OsIocReceiverPullCB")
            gr.printFile("void callback_{}_{}(void)".format(iocid, name))
            gr.printFile("{")
            gr.printFile("    PrintText(\"callback sucess\\r\\n\\0\");")
            gr.printFile("}\n")

    def generate_Sysioc_code(self, input_para, Is_pointer, iocType, data_re):
        ioc = self.ioc
        iocid = self.iocid
        iocDataProperties = self.iocDataProperties
        iocreceivers = self.iocsenders_or_iocreceivers
        for receiver in iocreceivers:
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + receiver ,"OsIocReceivingOsApplicationRef")
            gr.printFile("#define OS_OSAPP_{}_STOP_SEC_CODE".format(app))
            gr.printFile("#include \"OS_MemMap.h\"")
            gr.printFile("Std_ReturnType SysIocRead_{}_{}({})".format(iocid, receiver, input_para))
            gr.printFile("{")
            gr.printFile("    Std_ReturnType ret = IOC_E_OK;")
            gr.printFile("    if (ret == IOC_E_OK && (~(SystemObjectAutosar[_CoreID]->IocAutosar_r[{}].applicationsMask) & (1 << ExecutingApp[_CoreID])))".format(iocid))
            gr.printFile("    {")
            gr.printFile("        ret = IOC_E_NOK;")
            gr.printFile("    }")
            gr.printFile("    if (ret == IOC_E_OK)")
            gr.printFile("    {")
            
            iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocDataProperties[0] ,"OsIocDataTypeRef")
            if "*" not in iocType:     
                data_re = iocType 
            else:
                if not(iocType.endswith("*")):
                    ioctype_ptr = iocType.split(",")            
                    data_re = ioctype_ptr[1]
                else:
                    data_re = iocType.replace("*", "")
            
            if Is_pointer and not(iocType.endswith("*")): #type ref, uint16 length 情況
                ioctype_ptr = iocType.split(",")
                gr.printFile("        GetLock(&lock_{}, lock_bit);".format(iocid))
                gr.printFile("        IOCCB *cb = &icb[{}];".format(iocid))
                gr.printFile("        memcpy_j({}, length_1, sizeof(uint16), POP);".format(iocid))
                gr.printFile("        memcpy_j({}, ptr_1, *length_1, POP);".format(iocid))
                gr.printFile("        cb->head = cb->tail = 0;")
                gr.printFile("        ReleaseLock(&lock_{}, lock_bit);".format(iocid))
                gr.printFile("    }") 
            else:
                gr.printFile("        GetLock(&lock_{}, lock_bit);".format(iocid))
                gr.printFile("        IOCCB *cb = &icb[{}];".format(iocid))
                if Is_pointer: #type ref 情況
                    gr.printFile("        memcpy_j({}, ptr_1, sizeof({}), POP);".format(iocid, data_re))
                else: #type data
                    gr.printFile("        memcpy_j({}, data_1, sizeof({}), POP);".format(iocid, data_re))
                gr.printFile("        cb->head = cb->tail = 0;")
                gr.printFile("        ReleaseLock(&lock_{}, lock_bit);".format(iocid))
                gr.printFile("    }")   

            gr.printFile("#if (HOOK_ENABLE_ERRORHOOK == ENABLE)\n")
            gr.printFile("    if (ret != E_OK && !(systemFlag & (IN_ERROR_HOOK | IN_OSAPP_ERROR_HOOK | IN_OSAPP_SHUTDOWN_HOOK | IN_OSAPP_STARTUP_HOOK)))")
            gr.printFile("    {")
            gr.printFile("        /* System error hook */")
            gr.printFile("        systemFlag |= IN_ERROR_HOOK;")
            gr.printFile("        ErrorHook(ret);")
            gr.printFile("        systemFlag &= ~IN_ERROR_HOOK;")
            gr.printFile("        /* App error hook */\n")
            gr.printFile("#if (HOOK_ENABLE_OSAPP_ERRORHOOK == ENABLE)")
            gr.printFile("        if (ApplicationVar[ExecutingApp[_CoreID]].AppHookFuncArray.ErrorHookFunc != NULL)")
            gr.printFile("        {")
            gr.printFile("            APPErrorHook(ret);")
            gr.printFile("        }")
            gr.printFile("#endif")
            gr.printFile("    }")
            gr.printFile("#endif")
            gr.printFile("    return ret;")
            gr.printFile("}\n") 

#inherit from ioc_generator
class IocWriteGroup_generator(ioc_generator):
    def __init__(self, ioc, iocid, iocsenders, iocDataProperties):
        super().__init__(ioc, iocid, iocsenders, iocDataProperties)
        self.length_index = []
    
    def generate_parameters(self):
        ioc = self.ioc
        iocid = self.iocid
        iocDataProperties = self.iocDataProperties
        #sender data type
        i = 1
        input_para = ""
        length_index = []
        for iocData in iocDataProperties:
            iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
            if "*" not in iocType:
                input_para += (iocType + " data_" + str(i))
            else:
                if not(iocType.endswith("*")): #改動：type ref, uint16 length 情況
                    ioctype_ptr = iocType.split(",")            
                    input_para += ioctype_ptr[0] + " ptr_" + str(i) + ", uint16 length_" + str(i)
                    length_index.append(i)
                else: #改動：type ref 情況
                    input_para += iocType + " ptr_" + str(i)
            if iocData != iocDataProperties[-1]:
                input_para += ", "
            i += 1
        return input_para, None, iocType, None
    
    def generate_ioc_code(self, input_para, Is_pointer, iocType):
        ioc = self.ioc
        iocid = self.iocid
        iocDataProperties = self.iocDataProperties
        iocsenders = self.iocsenders_or_iocreceivers
        for sender in iocsenders:
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + sender ,"OsIocSendingOsApplicationRef")
            gr.printFile("#define OS_OSAPP_{}_START_SEC_CODE".format(app))
            gr.printFile("#include \"OS_MemMap.h\"")
            
            gr.printFile("Std_ReturnType IocWriteGroup_{}_{}({})".format(iocid, sender, input_para))
            gr.printFile("{")
            gr.printFile("    struct IOC_{}_struct d;".format(iocid))
            j = 1
            for iocData in iocDataProperties:
                iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                if "*" not in iocType:     
                    gr.printFile("    d.data_{} = data_{};".format(j, j))
                else:
                    if not(iocType.endswith("*")): #改動：type ref, uint16 length 情況
                        ioctype_ptr = iocType.split(",")
                        gr.printFile("    d.ptr_{} = ptr_{};".format(j, j))            
                        gr.printFile("    d.length_{} = length_{};".format(j, j))
                    else: #改動：type ref 情況
                        gr.printFile("    d.ptr_{} = ptr_{};".format(j, j))
                j += 1

            gr.printFile("    SysServiceParaType para;")
            gr.printFile("    para.serviceID = SERVICE_IOC;")
            gr.printFile("    para.para1 = {}; // ioc channel".format(iocid))
            gr.printFile("    para.para2 = &d; // parameter")   
            gr.printFile("    para.para3 = IOC_SEND_{}_{};".format(iocid, sender))
            gr.printFile("    para.result = IOC_E_OK;\n")

            gr.printFile("    pushStack(&para);")
            gr.printFile("    sysCallSystemService();")
            gr.printFile("    popStack(&para);")
            gr.printFile("    return para.result;")
            gr.printFile("}\n")

    def generate_Sysioc_code(self, input_para, Is_pointer, iocType, data_send):
        ioc = self.ioc
        iocid = self.iocid
        iocDataProperties = self.iocDataProperties
        iocsenders = self.iocsenders_or_iocreceivers
        length_index = self.length_index
        for sender in iocsenders:
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + sender ,"OsIocSendingOsApplicationRef")
            gr.printFile("#define OS_OSAPP_{}_STOP_SEC_CODE".format(app))
            gr.printFile("#include \"OS_MemMap.h\"\n")
        
            gr.printFile("Std_ReturnType SysIocWriteGroup_{}_{}({})".format(iocid, sender, input_para))
            gr.printFile("{")
            gr.printFile("    Std_ReturnType ret = IOC_E_OK;")
            gr.printFile("    if (ret == IOC_E_OK && (~(SystemObjectAutosar[_CoreID]->IocAutosar_s[{}].applicationsMask) & (1 << ExecutingApp[_CoreID])))".format(iocid))
            gr.printFile("    {")
            gr.printFile("        ret = IOC_E_NOK;")
            gr.printFile("    }")
            gr.printFile("    if (ret == IOC_E_OK)")
            gr.printFile("    {")
            gr.printFile("        GetLock(&lock_{}, lock_bit);".format(iocid))
            gr.printFile("        IOCCB *cb = &icb[{}];".format(iocid))   
            if "length" in input_para:
                gr.printFileSpace("        int length = ")       
                for index in length_index:
                    gr.printFileSpace(f"length_{index}")
                    if index != length_index[-1]:
                        gr.printFileSpace(" + ")
                gr.printFile(";")
                gr.printFile("        if (length == 0 || length > cb->length)")
                gr.printFile("        {")
                gr.printFile("            ret = IOC_E_LENGTH;")
                gr.printFile("        }")
            gr.printFile("        if (ret == IOC_E_OK)")
            gr.printFile("        {")
            j = 1
            for iocData in iocDataProperties:
                iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                if "*" not in iocType:     
                    gr.printFile("            memcpy_j({}, &data_{}, sizeof({}), PUSH);".format(iocid, j, iocType))
                else:
                    if not(iocType.endswith("*")): #type ref, uint16 length 
                        ioctype_ptr = iocType.split(",")
                        gr.printFile("            memcpy_j({}, &length_{}, sizeof(uint16), PUSH);".format(iocid, j))
                        gr.printFile("            memcpy_j({}, ptr_{}, length_{}, PUSH);".format(iocid, j , j))

                    else:
                        gr.printFile("            memcpy_j({}, ptr_{}, sizeof({}), PUSH);".format(iocid, j , iocType.replace("*", "")))
                j += 1
            gr.printFile("            cb->tail = cb->head = 0;")
            gr.printFile("            if (cb->callbackFlag == 1)")
            gr.printFile("            {")
            gr.printFile("                for (int i = 0; i < cb->channel_receive_num; i++)")
            gr.printFile("                {")
            gr.printFile("                    SetCallbackfunctionAction(cb->receiver[i].appID, cb->receiver[i].callback);")
            gr.printFile("                }")
            gr.printFile("            }")
            gr.printFile("        }")
            
            gr.printFile("        ReleaseLock(&lock_{}, lock_bit);".format(iocid))
            gr.printFile("    }")
        
        
            gr.printFile("#if (HOOK_ENABLE_ERRORHOOK == ENABLE)\n")
            gr.printFile("    if (ret != E_OK && !(systemFlag & (IN_ERROR_HOOK | IN_OSAPP_ERROR_HOOK | IN_OSAPP_SHUTDOWN_HOOK | IN_OSAPP_STARTUP_HOOK)))")
            gr.printFile("    {")
            gr.printFile("        /* System error hook */")
            gr.printFile("        systemFlag |= IN_ERROR_HOOK;")
            gr.printFile("        ErrorHook(ret);")
            gr.printFile("        systemFlag &= ~IN_ERROR_HOOK;")
            gr.printFile("        /* App error hook */\n")
            gr.printFile("#if (HOOK_ENABLE_OSAPP_ERRORHOOK == ENABLE)")
            gr.printFile("        if (ApplicationVar[ExecutingApp[_CoreID]].AppHookFuncArray.ErrorHookFunc != NULL)")
            gr.printFile("        {")
            gr.printFile("            APPErrorHook(ret);")
            gr.printFile("        }")
            gr.printFile("#endif")
            gr.printFile("    }")
            gr.printFile("#endif")

            gr.printFile("    return ret;")
            gr.printFile("}\n")

#inherit from ioc_generator
class IocReadGroup_generator(ioc_generator):
    def __init__(self, ioc, iocid, iocreceivers, iocDataProperties):
        super().__init__(ioc, iocid, iocreceivers, iocDataProperties)

    def generate_parameters(self):
        ioc = self.ioc
        iocid = self.iocid
        iocDataProperties = self.iocDataProperties
        #receive data
        i = 1
        input_para = ""
        Is_pointer = False
        for iocData in iocDataProperties:
            iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
            if "*" not in iocType:     
                input_para += (iocType + "* data_" + str(i))
            else:
                if not(iocType.endswith("*")): #改動：type ref, uint16 length 情況
                    ioctype_ptr = iocType.split(",")
                    input_para += ioctype_ptr[0] + " ptr_" + str(i) + ", uint16* length_" + str(i)
                else: #改動：type ref 情況
                    input_para += iocType + " ptr_" + str(i)
                Is_pointer = True
            
            if iocData != iocDataProperties[-1]:
                input_para += ", "
            i += 1
        return input_para, Is_pointer, iocType, None

    def generate_ioc_code(self, input_para, Is_pointer, iocType):
        ioc = self.ioc
        iocid = self.iocid
        iocDataProperties = self.iocDataProperties
        iocreceivers = self.iocsenders_or_iocreceivers
        for receiver in iocreceivers:
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + receiver ,"OsIocReceivingOsApplicationRef")
            gr.printFile("#define OS_OSAPP_{}_START_SEC_CODE".format(app))
            gr.printFile("#include \"OS_MemMap.h\"")
            gr.printFile("Std_ReturnType IocReadGroup_{}_{}({})".format(iocid, receiver, input_para))
            gr.printFile("{")
            gr.printFile("    struct IOC_{}_struct d;".format(iocid))
            j = 1
            for iocdata in iocDataProperties:
                iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocdata ,"OsIocDataTypeRef")
                if "*" not in iocType:
                        gr.printFile("    d.data_{}_r = data_{};".format(j, j))
                else:
                    if not(iocType.endswith("*")): # type ref, uint16 length
                        ioctype_ptr = iocType.split(",")
                        gr.printFile("    d.ptr_{} = ptr_{};".format(j, j))
                        gr.printFile("    d.length_{}_r = length_{};".format(j, j))
                    else: #type ref 
                        gr.printFile("    d.ptr_{} = ptr_{};".format(j, j))
                j += 1

            gr.printFile("    SysServiceParaType para;")
            gr.printFile("    para.serviceID = SERVICE_IOC;")
            gr.printFile("    para.para1 = {}; // ioc channel".format(iocid))
            gr.printFile("    para.para2 = &d; // parameter")   
            gr.printFile("    para.para3 = IOC_RECEIVER_{}_{};".format(iocid, receiver))
            gr.printFile("    para.result = IOC_E_OK;\n")

            gr.printFile("    pushStack(&para);")
            gr.printFile("    sysCallSystemService();")
            gr.printFile("    popStack(&para);")
            gr.printFile("    return para.result;")
            gr.printFile("}\n")

            name = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + receiver ,"OsIocReceiverPullCB")
            gr.printFile("void callback_{}_{}(void)".format(iocid, name))
            gr.printFile("{")
            gr.printFile("    PrintText(\"callback sucess\\r\\n\\0\");")
            gr.printFile("}\n")

    def generate_Sysioc_code(self, input_para, Is_pointer, iocType, data_re):
        ioc = self.ioc
        iocid = self.iocid
        iocDataProperties = self.iocDataProperties
        iocreceivers = self.iocsenders_or_iocreceivers
        for receiver in iocreceivers:
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + receiver ,"OsIocReceivingOsApplicationRef")
            gr.printFile("#define OS_OSAPP_{}_STOP_SEC_CODE".format(app))
            gr.printFile("#include \"OS_MemMap.h\"")
            gr.printFile("Std_ReturnType SysIocReadGroup_{}_{}({})".format(iocid, receiver, input_para))
            gr.printFile("{")
            gr.printFile("    Std_ReturnType ret = IOC_E_OK;")
            gr.printFile("    if (ret == IOC_E_OK && (~(SystemObjectAutosar[_CoreID]->IocAutosar_r[{}].applicationsMask) & (1 << ExecutingApp[_CoreID])))".format(iocid))
            gr.printFile("    {")
            gr.printFile("        ret = IOC_E_NOK;")
            gr.printFile("    }")
            gr.printFile("    if (ret == IOC_E_OK)")
            gr.printFile("    {")
            
            gr.printFile("        GetLock(&lock_{}, lock_bit);".format(iocid))
            gr.printFile("        IOCCB *cb = &icb[{}];".format(iocid))
            j = 1
            for iocData in iocDataProperties:
                iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                if "*" not in iocType:     
                    gr.printFile("        memcpy_j({}, data_{}, sizeof({}), POP);".format(iocid, j, iocType))
                else:
                    if not(iocType.endswith("*")): #type ref, uint16 length 
                        ioctype_ptr = iocType.split(",")
                        gr.printFile("        memcpy_j({}, length_{}, sizeof(uint16), POP);".format(iocid, j))
                        gr.printFile("        memcpy_j({}, ptr_{}, *length_{}, POP);".format(iocid, j , j))
                    else:
                        gr.printFile("        memcpy_j({}, ptr_{}, sizeof({}), POP);".format(iocid, j , iocType.replace("*", "")))
                j += 1
            
            gr.printFile("        cb->head = cb->tail = 0;")
            gr.printFile("        ReleaseLock(&lock_{}, lock_bit);".format(iocid))
            gr.printFile("    }") 


            gr.printFile("#if (HOOK_ENABLE_ERRORHOOK == ENABLE)\n")
            gr.printFile("    if (ret != E_OK && !(systemFlag & (IN_ERROR_HOOK | IN_OSAPP_ERROR_HOOK | IN_OSAPP_SHUTDOWN_HOOK | IN_OSAPP_STARTUP_HOOK)))")
            gr.printFile("    {")
            gr.printFile("        /* System error hook */")
            gr.printFile("        systemFlag |= IN_ERROR_HOOK;")
            gr.printFile("        ErrorHook(ret);")
            gr.printFile("        systemFlag &= ~IN_ERROR_HOOK;")
            gr.printFile("        /* App error hook */\n")
            gr.printFile("#if (HOOK_ENABLE_OSAPP_ERRORHOOK == ENABLE)")
            gr.printFile("        if (ApplicationVar[ExecutingApp[_CoreID]].AppHookFuncArray.ErrorHookFunc != NULL)")
            gr.printFile("        {")
            gr.printFile("            APPErrorHook(ret);")
            gr.printFile("        }")
            gr.printFile("#endif")
            gr.printFile("    }")
            gr.printFile("#endif")
            gr.printFile("    return ret;")
            gr.printFile("}\n") 

def generate_IOC_api(ioc, iocids):
    for iocid in iocids:
        iocDataProperties = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocDataProperties")
        iocsenders = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocSenderProperties")
        iocreceivers = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocReceiverProperties")
        length = config.getValue("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocBufferLength") 
        send_or_write_generator = None
        receive_or_read_generator = None
        #OsIocBufferLength 有沒有設定，用來判斷是 "event" or "data" sementics。
        if length != False:
            #use multiplicity of iocDataProperties 做是否為 group 的判斷
            if len(iocDataProperties) == 1:
                send_or_write_generator = IocSend_senderId_generator(ioc, iocid, iocsenders, iocDataProperties)
                receive_or_read_generator = IocReceive_generator(ioc, iocid, iocreceivers, iocDataProperties)
            elif len(iocDataProperties) > 1:
                send_or_write_generator = IocSendGroup_generator(ioc, iocid, iocsenders, iocDataProperties)
                receive_or_read_generator = IocReceiveGroup_generator(ioc, iocid, iocreceivers, iocDataProperties)
        else:
            if len(iocDataProperties) == 1:
                send_or_write_generator = IocWrite_senderId_generator(ioc, iocid, iocsenders, iocDataProperties)
                receive_or_read_generator = IocRead_receiverId_generator(ioc, iocid, iocreceivers, iocDataProperties)
            elif len(iocDataProperties) > 1:
                send_or_write_generator = IocWriteGroup_generator(ioc, iocid, iocsenders, iocDataProperties)
                receive_or_read_generator = IocReadGroup_generator(ioc, iocid, iocreceivers, iocDataProperties)
        send_or_write_generator.generate_IOC_api()
        receive_or_read_generator.generate_IOC_api()


def main():
    gr.genfile = open("../kernel/Ioc.c",'w')
    generate_include_sentence()
    generate_memcpy_fn()

    ioc = config.getValue("/AUTOSAR","OsIoc")
    apps = config.getList("/AUTOSAR","OsApplication")
    iocids = config.getList("/AUTOSAR/" + ioc,"OsIocCommunication")

    if ioc != False:
        generate_system_call(ioc, iocids)
        generate_lockBit_and_buffer(ioc, iocids)

        gr.printFile("extern CoreIdType _CoreID;")
        gr.printFile("static uint16 lock_bit = 7;\n")

        generate_callback_fn()
        generate_ReceiverType(ioc, iocids)
        generate_IocAutosarType(ioc, iocids)
        generate_IOCCB(ioc, iocids)
        
        generate_IOC_api(ioc, iocids)

if __name__ == "__main__":
    main()


