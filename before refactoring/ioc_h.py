from generator.config import config 
from generator import globals as gr

global config
gr.genfile = open("../kernel/Ioc.h",'w')

gr.printFile("#ifndef IOC_H")
gr.printFile("#define IOC_H")
gr.printFile("/* This file content the generated configuration of ioc */")
gr.printFile("/*==================[inclusions]=============================================*/")
gr.printFile("#include \"typedefine.h\"")
gr.printFile("/*==================[macros]=================================================*/")

ioc = config.getValue("/AUTOSAR","OsIoc")
apps = config.getList("/AUTOSAR","OsApplication")
structs = config.getList("/AUTOSAR","STRUCTURE")
if ioc != False:
    iocids = config.getList("/AUTOSAR/" + ioc,"OsIocCommunication")
i = 0 
j = 10
if ioc != False:
    for iocid in iocids: 
        length = config.getValue("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocBufferLength")
        iocDataProperties = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocDataProperties")
        iocsenders = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocSenderProperties")
        iocreceivers = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocReceiverProperties")
        for sender in iocsenders:
            gr.printFile("#define IOC_SEND_{}_{} {}".format(iocid, sender, i))
            i += 1
        for receiver in iocreceivers:
            gr.printFile("#define IOC_RECEIVER_{}_{} {}".format(iocid, receiver, j))
            j += 1
    gr.printFile("#define IOC_EMPTY 20\n")








    #
    gr.printFile("/*define*/")
    gr.printFile("typedef struct{")
    gr.printFile("    ApplicationType appID;")
    gr.printFile("    void (*callback)(void);")
    gr.printFile("}ReceiverType;\n")

    gr.printFile("typedef struct IOCCB{")
    gr.printFile("    uint32 head; //internel buffer index")
    gr.printFile("    uint32 tail; //internel buffer index")
    gr.printFile("    uint32 length; // internel buffer length")
    gr.printFile("    uint32 channel_receive_num; // the number of receiver")
    gr.printFile("    ReceiverType *receiver; // point to array that store the receiver and callback function informationl")
    gr.printFile("    uint8 callbackFlag; // if the callback function is set, set this flag")
    gr.printFile("    uint8 lostFlag; // if the data is lost, set this flag")
    gr.printFile("    uint32 *buffer; // point to the internel buffer")
    gr.printFile("}IOCCB;\n")

    gr.printFile("#define POP 0")
    gr.printFile("#define PUSH 1")
    gr.printFile("Std_ReturnType IOC_API(int id, void* input_data,int flag);")
    gr.printFile("Std_ReturnType SetCallbackfunctionAction(ApplicationType ,void (*callback)(void));")
    gr.printFile("void memcpy_j(int iocid, void *data, int size, int flag);\n")




    #/*==================[external functions declaration]=========================*/
    gr.printFile("#define IOCID_COUNT {}\n".format(len(iocids)))
    gr.printFile("extern IocAutosarType Ioc_channel_sender[IOCID_COUNT];")
    gr.printFile("extern IocAutosarType Ioc_channel_receiver[IOCID_COUNT];")

    for iocid in iocids:
        gr.printFile("#define {} {}".format(iocid, iocids.index(iocid)))

    gr.printFile("extern IocAutosarType Ioc_channel_sender[IOCID_COUNT];")
    gr.printFile("extern IocAutosarType Ioc_channel_receiver[IOCID_COUNT];")
        
    for iocid in iocids:       
        iocDataProperties = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocDataProperties")
        i = 1
        gr.printFile("struct IOC_{}_struct{}".format(iocid, "{"))
        for iocData in iocDataProperties:
            iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
            if "*" in iocType:   
                ioctype_ptr = iocType.split(",")
                gr.printFile("    {} ptr_{};".format(ioctype_ptr[0], i))

                gr.printFile("    union{")
                gr.printFile("        {} length_{};".format(ioctype_ptr[1], i))
                gr.printFile("        {}* length_{}_r;".format(ioctype_ptr[1], i))
                gr.printFile("    };")
                i += 1
            else:
                gr.printFile("    union{")
                gr.printFile("        {} data_{};".format(iocType, i))
                gr.printFile("        {}* data_{}_r;".format(iocType, i))
                gr.printFile("    };")
                i += 1

        gr.printFile("};")

    gr.printFile("extern IOCCB icb[IOCID_COUNT];\n")

    for iocid in iocids: 
        length = config.getValue("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocBufferLength")
        iocDataProperties = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocDataProperties")
        iocsenders = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocSenderProperties")
        iocreceivers = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocReceiverProperties")
        
        if length != False:
            gr.printFile("extern uint16 lock_{} ;".format(iocid))    
            gr.printFile("extern uint8 buffer_{}[{}];".format(iocid, length))
            count = config.getCount("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocReceiverProperties")
            gr.printFile("extern ReceiverType receiver_{}[{}] ;\n".format(iocid, count))     
            
            if len(iocDataProperties) > 1:
                send_datatype = ""
                receiver_datatype = ""
                for iocData in iocDataProperties:
                    iocdataType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                    send_datatype += iocdataType
                    receiver_datatype += (iocdataType + "*")
                    if iocData != iocDataProperties[-1]:
                        send_datatype += ", "
                        receiver_datatype += ", "
                for sender in iocsenders:
                    gr.printFile("Std_ReturnType IocSendGroup_{}_{}({});".format(iocid, sender, send_datatype))
                    gr.printFile("Std_ReturnType SysIocSendGroup_{}_{}({});".format(iocid, sender, send_datatype))
                for receiver in iocreceivers:
                    gr.printFile("Std_ReturnType IocReceiveGroup_{}_{}({});".format(iocid, receiver, receiver_datatype))
                    gr.printFile("Std_ReturnType SysIocReceiveGroup_{}_{}({});".format(iocid, receiver, receiver_datatype))
                
                gr.printFile("Std_ReturnType IocEmptyQueue_{}(void);".format(iocid))
                gr.printFile("Std_ReturnType SysIocEmptyQueue_{}(void);".format(iocid))
            elif len(iocDataProperties) == 1:
                iocDataProperty = config.getValue("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocDataProperties")
                iocdataType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocDataProperty ,"OsIocDataTypeRef")

                for sender in iocsenders:
                    gr.printFile("Std_ReturnType IocSend_{}_{}({});".format(iocid, sender, iocdataType))
                    gr.printFile("Std_ReturnType SysIocSend_{}_{}({});\n".format(iocid, sender, iocdataType))
                if "*" in iocdataType:
                    ioctype_ptr = iocdataType.split(",")
                    gr.printFile("Std_ReturnType IocReceive_{}_{}({}, {}*);".format(iocid, receiver, ioctype_ptr[0], ioctype_ptr[1]))
                    gr.printFile("Std_ReturnType SysIocReceive_{}_{}({}, {}*);\n".format(iocid, receiver, ioctype_ptr[0], ioctype_ptr[1])) 
                
                else:
                    for receiver in iocreceivers:  
                        gr.printFile("Std_ReturnType IocReceive_{}_{}({});".format(iocid, receiver, iocdataType))
                        gr.printFile("Std_ReturnType SysIocReceive_{}_{}({});\n".format(iocid, receiver, iocdataType))
                gr.printFile("Std_ReturnType IocEmptyQueue_{}(void);".format(iocid))
                gr.printFile("Std_ReturnType SysIocEmptyQueue_{}(void);\n".format(iocid))
        else:
            iocDataProperties = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocDataProperties")
            iocsenders = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocSenderProperties")
            iocreceivers = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocReceiverProperties")
            if iocDataProperties != []:
                send_datatype = ""
                receiver_datatype = ""
                for iocData in iocDataProperties:
                    iocdataType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
                    send_datatype += iocdataType
                    receiver_datatype += (iocdataType + "*")
                    
                    if iocData != iocDataProperties[-1]:
                        send_datatype += iocdataType  + ", "
                        receiver_datatype += iocdataType  + ", "
                
                for sender in iocsenders:
                    gr.printFile("Std_ReturnType IocWrite_{}_{}({});".format(iocid, sender, send_datatype))
                    gr.printFile("Std_ReturnType SysIocWrite_{}_{}({});".format(iocid, sender, send_datatype))
                for receiver in iocreceivers:
                    gr.printFile("Std_ReturnType IocRead_{}_{}({});".format(iocid, receiver, receiver_datatype))
                    gr.printFile("Std_ReturnType SysIocRead_{}_{}({});".format(iocid, receiver, receiver_datatype))



    gr.printFile("")
    for iocid in iocids:
        iocReceiverProperties = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocReceiverProperties")
        for iocReceiver in iocReceiverProperties:
            name = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocReceiver ,"OsIocReceiverPullCB")
            if name != False:    
                gr.printFile("void callback_{}_{}(void);".format(iocid, name))   

    gr.printFile("#endif")