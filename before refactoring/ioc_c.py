from generator.config import config 
from generator import globals as gr
#import generator.generators as gr


global config
gr.genfile = open("../kernel/Ioc.c",'w')

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

ioc = config.getValue("/AUTOSAR","OsIoc")
apps = config.getList("/AUTOSAR","OsApplication")
iocids = []

if ioc != False:
    iocids = config.getList("/AUTOSAR/" + ioc,"OsIocCommunication")
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
        if length != False:
            if len(iocDataProperties) > 1:
                send_datatype = ""
                receiver_datatype = ""
                i = 1
                for iocData in iocDataProperties:
                    iocdataType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                        
                    if "*" not in iocdataType:
                        send_datatype += ("d-> data_" + str(i))
                        receiver_datatype += ("d-> data_" + str(i) + "_r")
                        i += 1
                        if iocData != iocDataProperties[-1]:
                            send_datatype += ", "
                            receiver_datatype += ", "
                        
                    else:
                        send_datatype += ("d-> ptr_" + str(i) + ", " + "d->length_" + str(i))
                        receiver_datatype += ("d-> ptr_" + str(i) + "," + "d->length_" + str(i) + "_r")
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

            if len(iocDataProperties) == 1:
                send_datatype = ""
                receiver_datatype = ""
                iocDataProperty = config.getValue("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocDataProperties")
                iocdataType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocDataProperty ,"OsIocDataTypeRef")          
                if "*" not in iocdataType:
                    send_datatype = "d-> data_1"
                    receiver_datatype = "d-> data_1_r"
                        
                else:
                    send_datatype += ("d-> ptr_1, d->length_1")
                    receiver_datatype += ("d-> ptr_1, d->length_1_r")
                
                for sender in iocsenders:
                    gr.printFile("        if (flag == IOC_SEND_{}_{})".format(iocid, sender))
                    gr.printFile("        {")
                    gr.printFile("            return SysIocSend_{}_{}({});".format(iocid, sender, send_datatype))
                    gr.printFile("        }")
                
                for receiver in iocreceivers:
                    gr.printFile("        if (flag == IOC_RECEIVER_{}_{})".format(iocid, receiver))
                    gr.printFile("        {")
                    gr.printFile("            return SysIocReceive_{}_{}({});".format(iocid, receiver, receiver_datatype))
                    gr.printFile("        }")
                

                gr.printFile("        else if(flag == IOC_EMPTY)")
                gr.printFile("        {")
                gr.printFile("            return SysIocEmptyQueue_{}();".format(iocid))
                gr.printFile("        }")
                gr.printFile("        break;")
                gr.printFile("    }")    

        
        else:
            if len(iocDataProperties) >= 1:
                send_datatype = ""
                receiver_datatype = ""
                i = 1
                for iocData in iocDataProperties:
                    iocdataType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                        
                    if "*" not in iocdataType:
                        send_datatype += ("d-> data_" + str(i))
                        receiver_datatype += ("d-> data_" + str(i) + "_r")
                        i += 1
                        if iocData != iocDataProperties[-1]:
                            send_datatype += ", "
                            receiver_datatype += ", "
                        
                    else:
                        send_datatype += ("d-> ptr_" + str(i) + ", " + "d->length_" + str(i))
                        receiver_datatype += ("d-> ptr_" + str(i) + "," + "d->length_" + str(i) + "_r")
                        i += 1
                        if iocData != iocDataProperties[-1]:
                            send_datatype += ", "
                            receiver_datatype += ", "
                
                for sender in iocsenders:
                    gr.printFile("        if (flag == IOC_SEND_{}_{})".format(iocid, sender))
                    gr.printFile("        {")
                    gr.printFile("            return SysIocWrite_{}_{}({});".format(iocid, sender, send_datatype))
                    gr.printFile("        }")
                    i += 1
        
                for receiver in iocreceivers:
                    gr.printFile("        if (flag == IOC_RECEIVER_{}_{})".format(iocid, receiver))
                    gr.printFile("        {")
                    gr.printFile("            return SysIocRead_{}_{}({});".format(iocid, receiver, receiver_datatype))
                    gr.printFile("        }")
                gr.printFile("        break;")
                gr.printFile("    }")
    gr.printFile("    }")
    gr.printFile("}\n")

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
    gr.printFile("        GetLock(&CoreParaLock[CoreID], LOCKBIT);")
    gr.printFile("        CrossCoreServicePara[CoreID].serviceID = SERVICE_CALLBACKFUNCTION;")
    gr.printFile("        CrossCoreServicePara[CoreID].para1 = reveiverID;")
    gr.printFile("        CrossCoreServicePara[CoreID].para2 = callback;")
    gr.printFile("        // CrossCoreServicePara[reveiverID].App = ExecutingApp[_CoreID];\n")

    gr.printFile("       CoreIntFlag[CoreID] = 1;")
    gr.printFile("        InterruptToCore(CoreID);")
    gr.printFile("        while (CoreIntFlag[CoreID] == 1)")
    gr.printFile("            ;")
    gr.printFile("        ReleaseLock(&CoreParaLock[CoreID], LOCKBIT);")
    gr.printFile("        disableCrossCoreISR();")
    gr.printFile("    }")
    gr.printFile("}\n\n")


    for iocid in iocids:
        gr.printFile("uint16 lock_{} = 0;".format(iocid))
        length = config.getValue("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocBufferLength")
        if length != False:
            gr.printFile("uint8 buffer_{}[{}];".format(iocid, length))
        else:
            gr.printFile("uint8 buffer_{}[100];".format(iocid))

    gr.printFile("extern CoreIdType _CoreID;")
    gr.printFile("static uint16 lock_bit = 7;\n")

    for iocid in iocids:
        iocDataProperties = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocDataProperties")
        iocsenders = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocSenderProperties")
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

    gr.printFile("IocAutosarType Ioc_channel_sender[IOCID_COUNT] = {")
    for iocid in iocids:
        iocsenders = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocSenderProperties")
        gr.printFileSpace("    0 ")
        for sender in iocsenders:
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + sender ,"OsIocSendingOsApplicationRef")
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
            app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocReceiver ,"OsIocReceivingOsApplicationRef")
            if receiver == iocreceivers[-1]:
                gr.printFile("| (1 << {}),".format(app))
            else:
                gr.printFileSpace("| (1 << {}) ".format(app))
    gr.printFile("};\n")


    gr.printFile("IOCCB icb[IOCID_COUNT] = {")
    for iocid in iocids:
        length = config.getValue("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocBufferLength")
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


    for iocid in iocids:
        iocDataProperties = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocDataProperties")
        iocsenders = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocSenderProperties")
        iocreceivers = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocReceiverProperties")

        i = 1
        data = ""
        Is_pointer = False
        if len(iocDataProperties) == 1:
            for iocData in iocDataProperties:
                iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                if "*" not in iocType:     
                    data += (iocType + " data_" + str(i))
                else:
                    ioctype_ptr = iocType.split(",")            
                    data = ioctype_ptr[0] + " ptr_" + str(i) + ", " + ioctype_ptr[1] + " length_" + str(i)
                    Is_pointer = True
                
                if iocData != iocDataProperties[-1]:
                    data += ", "
                i += 1

    ####################################################
            for sender in iocsenders:
                app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + sender ,"OsIocSendingOsApplicationRef")
                gr.printFile("#define OS_OSAPP_{}_START_SEC_CODE".format(app))
                gr.printFile("#include \"OS_MemMap.h\"")
                
                gr.printFile("Std_ReturnType IocSend_{}_{}({})".format(iocid, sender, data))
                gr.printFile("{")
                gr.printFile("    struct IOC_{}_struct d;".format(iocid))
                if Is_pointer:
                    gr.printFile("    d.ptr_1 = ptr_1;")
                    gr.printFile("    d.length_1 = length_1;")
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

                #sys
                gr.printFile("#define OS_OSAPP_{}_STOP_SEC_CODE".format(app))
                gr.printFile("#include \"OS_MemMap.h\"\n")
            
                gr.printFile("Std_ReturnType SysIocSend_{}_{}({})".format(iocid, sender, data))
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
                
                iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocDataProperties[0] ,"OsIocDataTypeRef")
                if "*" not in iocType:     
                    data_send = iocType 
                else:
                    ioctype_ptr = iocType.split(",")            
                    data_send = ioctype_ptr[1]
                
                if Is_pointer:
                    gr.printFile("        int length = length_1;")
                    gr.printFile("        if (length > cb->length)")
                    gr.printFile("        {")
                    gr.printFile("            ret = IOC_E_LENGTH;")
                    gr.printFile("        }")
                    gr.printFile("        if (ret == IOC_E_OK)")
                    gr.printFile("        {")
                    gr.printFile("            int data_size = length + sizeof({});".format(data_send))
                    gr.printFile("            int remain_size = (cb->head - cb->tail + cb->length - 1) % cb->length;")        
                    gr.printFile("            if (data_size > remain_size)")
                    gr.printFile("            {")
                    gr.printFile("                ret = IOC_E_LOST_DATA;")
                    gr.printFile("                cb->lostFlag = 1;")
                    gr.printFile("            }")
                    gr.printFile("        }")
                    gr.printFile("        if (ret == IOC_E_OK)")
                    gr.printFile("        {")
                    gr.printFile("            memcpy_j({}, &length_1, sizeof({}), PUSH);".format(iocid, data_send))
                    gr.printFile("            memcpy_j({}, ptr_1, length_1, PUSH);".format(iocid))
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




            #receiver data type
            i = 1
            for iocData in iocDataProperties:
                iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                if "*" not in iocType:     
                    data = (iocType + " *data_" + str(i))
                else:
                    ioctype_ptr = iocType.split(",")            
                    data = ioctype_ptr[0] + " ptr_" + str(i) + ", " + ioctype_ptr[1] + " *length_" + str(i)
                    Is_pointer = True
                
                if iocData != iocDataProperties[-1]:
                    data += ", "
                i += 1


            for receiver in iocreceivers:
                app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocReceiver ,"OsIocReceivingOsApplicationRef")
                gr.printFile("#define OS_OSAPP_{}_START_SEC_CODE".format(app))
                gr.printFile("#include \"OS_MemMap.h\"")
                gr.printFile("Std_ReturnType IocReceive_{}_{}({})".format(iocid, receiver, data))
                gr.printFile("{")
                gr.printFile("    struct IOC_{}_struct d;".format(iocid))
                if Is_pointer:
                    gr.printFile("    d.ptr_1 = ptr_1;")
                    gr.printFile("    d.length_1_r = length_1;")
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
                name = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocReceiver ,"OsIocReceiverPullCB")
                gr.printFile("void callback_{}_{}(void)".format(iocid, name))
                gr.printFile("{")
                gr.printFile("    int data;")
                gr.printFile("    PrintText(\"callback sucess\\r\\n\\0\");")
                gr.printFile("}\n")

                #sys
                gr.printFile("#define OS_OSAPP_{}_STOP_SEC_CODE".format(app))
                gr.printFile("#include \"OS_MemMap.h\"")
                gr.printFile("Std_ReturnType SysIocReceive_{}_{}({})".format(iocid, receiver, data))
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
                    ioctype_ptr = iocType.split(",")            
                    data_re = ioctype_ptr[1]
                
                if Is_pointer:
                    gr.printFile("        GetLock(&lock_{}, 1);".format(iocid))
                    gr.printFile("        IOCCB *cb = &icb[{}];".format(iocid))
                    gr.printFile("        if (cb->tail == cb->head)")
                    gr.printFile("        {")
                    gr.printFile("            ret = IOC_E_NO_DATA;")
                    gr.printFile("        }")
                    gr.printFile("        if (ret == IOC_E_OK)")
                    gr.printFile("        {")
                    gr.printFile("            memcpy_j({}, length_1, sizeof({}), POP);".format(iocid, data_re))
                    gr.printFile("            memcpy_j({}, ptr_1, *length_1, POP);".format(iocid))
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

    #####################################
        elif len(iocDataProperties) > 1:
            i = 1
            data = ""
            for iocData in iocDataProperties:
                iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                if "*" not in iocType:     
                    data += (iocType + " data_" + str(i))
                else:
                    ioctype_ptr = iocType.split(",")            
                    data += ioctype_ptr[0] + " ptr_" + str(i) + ", " + ioctype_ptr[1] + " length_" + str(i)
                
                if iocData != iocDataProperties[-1]:
                    data += ", "
                i += 1


            for sender in iocsenders:
                app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + sender ,"OsIocSendingOsApplicationRef")
                gr.printFile("#define OS_OSAPP_{}_START_SEC_CODE".format(app))
                gr.printFile("#include \"OS_MemMap.h\"")
                
                gr.printFile("Std_ReturnType IocSendGroup_{}_{}({})".format(iocid, sender, data))
                gr.printFile("{")
                gr.printFile("    struct IOC_{}_struct d;".format(iocid))
                j = 1
                for iocData in iocDataProperties:
                    iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                    if "*" not in iocType:     
                        gr.printFile("    d.data_{} = data_{};".format(j, j))
                        j += 1
                    else:
                        ioctype_ptr = iocType.split(",")
                        gr.printFile("    d.ptr_{} = ptr_{};".format(j, j))            
                        gr.printFile("    d.length_{} = length_{};".format(j, j))
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

                #sys
                gr.printFile("#define OS_OSAPP_{}_STOP_SEC_CODE".format(app))
                gr.printFile("#include \"OS_MemMap.h\"\n")
            
                gr.printFile("Std_ReturnType SysIocSendGroup_{}_{}({})".format(iocid, sender, data))
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
                gr.printFile("        int length = length_1;")       
                gr.printFile("        if (length_1 == 0 || length_1 > cb->length)")
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
                        ioctype_ptr = iocType.split(",")
                        gr.printFileSpace("length_{} + sizeof({})".format(j, ioctype_ptr[1]))
                    
                    j += 1 
                    if iocData != iocDataProperties[-1]:
                        gr.printFileSpace(" + ")
                    else:
                        gr.printFileSpace(";\n")

                gr.printFile("            int remain_size = (cb->head - cb->tail + cb->length - 1) % cb->length;")        
                gr.printFile("            if (data_size > remain_size)")
                gr.printFile("            {")
                gr.printFile("                cb->lostFlag = 1;")
                gr.printFile("                ReleaseLock(&lock_{}, lock_bit);".format(iocid))
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
                        ioctype_ptr = iocType.split(",")
                        gr.printFile("            memcpy_j({}, &length_{}, sizeof({}), PUSH);".format(iocid, j, ioctype_ptr[1]))
                        gr.printFile("            memcpy_j({}, ptr_{}, length_{}, PUSH);".format(iocid, j , j))
                    
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




            #receiver data type
            i = 1
            data = ""
            for iocData in iocDataProperties:
                iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                if "*" not in iocType:     
                    data += (iocType + " *data_" + str(i))
                else:
                    ioctype_ptr = iocType.split(",")            
                    data += ioctype_ptr[0] + " ptr_" + str(i) + ", " + ioctype_ptr[1] + " *length_" + str(i)
                
                if iocData != iocDataProperties[-1]:
                    data += ", "
                i += 1


            for receiver in iocreceivers:
                app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocReceiver ,"OsIocReceivingOsApplicationRef")
                gr.printFile("#define OS_OSAPP_{}_START_SEC_CODE".format(app))
                gr.printFile("#include \"OS_MemMap.h\"")
                gr.printFile("Std_ReturnType IocReceiveGroup_{}_{}({})".format(iocid, receiver, data))
                gr.printFile("{")
                gr.printFile("    struct IOC_{}_struct d;".format(iocid))
                j = 1
                for iocData in iocDataProperties:
                    iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                    if "*" not in iocType:     
                        gr.printFile("    d.data_{}_r = data_{};".format(j, j))
                    else:
                        ioctype_ptr = iocType.split(",")
                        gr.printFile("    d.ptr_{} = ptr_{};".format(j, j))            
                        gr.printFile("    d.length_{}_r = length_{};".format(j, j))
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
                name = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocReceiver ,"OsIocReceiverPullCB")
                gr.printFile("void callback_{}_{}(void)".format(iocid, name))
                gr.printFile("{")
                gr.printFile("    int data;")
                gr.printFile("    PrintText(\"callback sucess\\r\\n\\0\");")
                gr.printFile("}\n")

                #sys
                gr.printFile("#define OS_OSAPP_{}_STOP_SEC_CODE".format(app))
                gr.printFile("#include \"OS_MemMap.h\"")
                gr.printFile("Std_ReturnType SysIocReceiveGroup_{}_{}({})".format(iocid, receiver, data))
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
                    ioctype_ptr = iocType.split(",")            
                    data_re = ioctype_ptr[1]
                
                gr.printFile("        GetLock(&lock_{}, 1);".format(iocid))
                gr.printFile("        IOCCB *cb = &icb[{}];".format(iocid))
                gr.printFile("        if (cb->head == cb->tail)")
                gr.printFile("        {")
                gr.printFile("            ReleaseLock(&lock_{}, lock_bit);".format(iocid))
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
                        ioctype_ptr = iocType.split(",")
                        gr.printFile("            memcpy_j({}, length_{}, sizeof({}), POP);".format(iocid, j, ioctype_ptr[1]))
                        gr.printFile("            memcpy_j({}, ptr_{}, *length_{}, POP);".format(iocid, j , j))
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
        
    ############################################################
        elif iocDataProperties == []:
            for iocData in iocDataProperties:
                iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                if "*" not in iocType:     
                    data += (iocType + " data_" + str(i))
                else:
                    ioctype_ptr = iocType.split(",")            
                    data = ioctype_ptr[0] + " ptr_" + str(i) + ", " + ioctype_ptr[1] + " length_" + str(i)
                    Is_pointer = True
                
                if iocData != iocDataProperties[-1]:
                    data += ", "
                i += 1


            for sender in iocsenders:
                app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + sender ,"OsIocSendingOsApplicationRef")
                gr.printFile("#define OS_OSAPP_{}_START_SEC_CODE".format(app))
                gr.printFile("#include \"OS_MemMap.h\"")
                
                gr.printFile("Std_ReturnType IocWrite_{}_{}({})".format(iocid, sender, data))
                gr.printFile("{")
                gr.printFile("    struct IOC_{}_struct d;".format(iocid))
                if Is_pointer:
                    gr.printFile("    d.ptr_1 = ptr_1;")
                    gr.printFile("    d.length_1 = length_1;")
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

                #sys
                gr.printFile("#define OS_OSAPP_{}_STOP_SEC_CODE".format(app))
                gr.printFile("#include \"OS_MemMap.h\"\n")
            
                gr.printFile("Std_ReturnType SysIocWrite_{}_{}({})".format(iocid, sender, data))
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
                else:
                    ioctype_ptr = iocType.split(",")            
                    data_send = ioctype_ptr[1]
                
                if Is_pointer:
                    gr.printFile("        if (length == 0 || length > cb->length)")
                    gr.printFile("        {")
                    gr.printFile("            ret = IOC_E_LENGTH;")
                    gr.printFile("        }")
                    gr.printFile("        if (ret == IOC_E_OK)")
                    gr.printFile("        {")
                    gr.printFile("            memcpy_j({}, &length_1, sizeof({}), PUSH);".format(iocid, data_send))
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
                else:
                    gr.printFile("        if (ret == IOC_E_OK)")
                    gr.printFile("        {")
                    gr.printFile("            memcpy_j({}, &data, sizeof({}), PUSH);\n".format(iocid, data_send))
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




            #receiver data type
            i = 1
            for iocData in iocDataProperties:
                iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                if "*" not in iocType:     
                    data = (iocType + " *data_" + str(i))
                else:
                    ioctype_ptr = iocType.split(",")            
                    data = ioctype_ptr[0] + " ptr_" + str(i) + ", " + ioctype_ptr[1] + " *length_" + str(i)
                    Is_pointer = True
                
                if iocData != iocDataProperties[-1]:
                    data += ", "
                i += 1


            for receiver in iocreceivers:
                app = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocReceiver ,"OsIocReceivingOsApplicationRef")
                gr.printFile("#define OS_OSAPP_{}_START_SEC_CODE".format(app))
                gr.printFile("#include \"OS_MemMap.h\"")
                gr.printFile("Std_ReturnType IocRead_{}_{}({})".format(iocid, receiver, data))
                gr.printFile("{")
                gr.printFile("    struct IOC_{}_struct d;".format(iocid))
                if Is_pointer:
                    gr.printFile("    d.ptr = ptr_1;")
                    gr.printFile("    d.length_1_r = length_1;")
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

                name = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocReceiver ,"OsIocReceiverPullCB")
                gr.printFile("void callback_{}_{}(void)".format(iocid, name))
                gr.printFile("{")
                gr.printFile("    PrintText(\"callback sucess\\r\\n\\0\");")
                gr.printFile("}\n")

                #sys
                gr.printFile("#define OS_OSAPP_{}_STOP_SEC_CODE".format(app))
                gr.printFile("#include \"OS_MemMap.h\"")
                gr.printFile("Std_ReturnType SysIocRead_{}_{}({})".format(iocid, receiver, data))
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
                    ioctype_ptr = iocType.split(",")            
                    data_re = ioctype_ptr[1]
                
                if Is_pointer:
                    gr.printFile("        GetLock(&lock_{}, 1);".format(iocid))
                    gr.printFile("        IOCCB *cb = &icb[{}];".format(iocid))
                    gr.printFile("        memcpy_j({}, length_1, sizeof({}), POP);".format(iocid, data_re))
                    gr.printFile("        memcpy_j({}, ptr_1, *length_1, POP);".format(iocid))
                    gr.printFile("        cb->head = cb->tail = 0;")
                    gr.printFile("        ReleaseLock(&lock_{}, 1);".format(iocid))
                    gr.printFile("    }") 

                else:
                    gr.printFile("        GetLock(&lock_{}, lock_bit);".format(iocid))
                    gr.printFile("        IOCCB *cb = &icb[{}];".format(iocid))
                    gr.printFile("        memcpy_j({}, data_1, sizeof({}), POP);".format(iocid, data_re))
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