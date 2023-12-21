from pickle import FALSE
from generator.config import config 
from generator import globals as gr

global config

def sender_receiver_and_empty_macros(ioc, iocids):
    i = 0 
    j = 10
    for iocid in iocids:
        # length = config.getValue("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocBufferLength")
        # iocDataProperties = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocDataProperties")
        iocsenders = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocSenderProperties")
        iocreceivers = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocReceiverProperties")
        for sender in iocsenders:
            gr.printFile("#define IOC_SEND_{}_{} {}".format(iocid, sender, i))
            i += 1
        for receiver in iocreceivers:
            gr.printFile("#define IOC_RECEIVER_{}_{} {}".format(iocid, receiver, j))
            j += 1
    gr.printFile("#define IOC_EMPTY 20\n")

def ReceiverType_and_IOCCB_struct():
    gr.printFile("/*")
    gr.printFile("per channel has one IOCCB, with IOCCB ")
    gr.printFile("we can get the  information of the communication of channel")
    gr.printFile("*/")

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
    gr.printFile("    uint8* buffer; // point to the internel buffer")
    gr.printFile("}IOCCB;\n")

def iocid_count_and_iocid_macros(iocids):
    gr.printFile("#define IOCID_COUNT {}\n".format(len(iocids)))
    for iocid in iocids:
        gr.printFile("#define {} {}".format(iocid, iocids.index(iocid)))

def struct_for_IOC_api(ioc, iocids):
    for iocid in iocids:
        iocDataProperties = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocDataProperties")
        i = 1
        gr.printFile("struct IOC_{}_struct{}".format(iocid, "{"))
        for iocData in iocDataProperties:
            iocType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
            if "*" in iocType:
                if "," in iocType: #type ref, uint16 length
                    ioctype_ptr = iocType.split(",")
                    gr.printFile("    {} ptr_{};".format(ioctype_ptr[0], i))

                    gr.printFile("    union{")
                    gr.printFile("        uint16 length_{};".format(i))
                    gr.printFile("        uint16* length_{}_r;".format(i))
                    gr.printFile("    };")
                else: #struct IOC for type ref
                    gr.printFile("    {} ptr_{};".format(iocType, i))
            else:
                gr.printFile("    union{")
                gr.printFile("        {} data_{};".format(iocType, i))
                gr.printFile("        {}* data_{}_r;".format(iocType, i))
                gr.printFile("    };")
            i += 1
        gr.printFile("};")

def IocSendGroup_IocReceiveGroup_IocEmptyQueue_and_related_Syscall(ioc, iocid, iocsenders, iocreceivers, iocDataProperties):
    send_datatype = ""
    receiver_datatype = ""
    for iocData in iocDataProperties:
        iocdataType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
        if ("*" in iocdataType) and not(iocdataType.endswith("*")): #type ref, uint16 length
            ioctype_ptr = iocdataType.split(",")
            send_datatype += ioctype_ptr[0] + ", uint16"
            receiver_datatype += ioctype_ptr[0] + ", uint16*"
        else:
            send_datatype += iocdataType
            receiver_datatype += iocdataType
            if not("*" in iocdataType):
                receiver_datatype += "*"
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
    gr.printFile("Std_ReturnType SysIocEmptyQueue_{}(void);\n".format(iocid))

def IocSend_IocReceive_IocEmptyQueue_and_related_Syscall(ioc, iocid, iocsenders):
    iocDataProperty = config.getValue("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocDataProperties")
    iocdataType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocDataProperty ,"OsIocDataTypeRef")

    for sender in iocsenders: #改動：調整整段 IocSend 生成判斷。
        if "*" in iocdataType:
            if "," in iocdataType: #有 length
                ioctype_ptr = iocdataType.split(",")
                gr.printFile("Std_ReturnType IocSend_{}_{}({}, uint16);".format(iocid, sender, ioctype_ptr[0]))
                gr.printFile("Std_ReturnType SysIocSend_{}_{}({}, uint16);".format(iocid, sender, ioctype_ptr[0]))
            else: 
                gr.printFile("Std_ReturnType IocSend_{}_{}({});".format(iocid, sender, iocdataType))
                gr.printFile("Std_ReturnType SysIocSend_{}_{}({});".format(iocid, sender, iocdataType))
        else:
            gr.printFile("Std_ReturnType IocSend_{}_{}({});".format(iocid, sender, iocdataType))
            gr.printFile("Std_ReturnType SysIocSend_{}_{}({});".format(iocid, sender, iocdataType))

    #IocReceive only support N:1 (one receiver)
    if "*" in iocdataType:
        if "," in iocdataType: #type ref, unit16 length
            ioctype_ptr = iocdataType.split(",")
            gr.printFile("Std_ReturnType IocReceive_{}({},uint16*);".format(iocid, ioctype_ptr[0])) #改動：拿掉 receiverID
            gr.printFile("Std_ReturnType SysIocReceive_{}({},uint16*);".format(iocid, ioctype_ptr[0])) #改動：拿掉 receiverID
        else: #type ref
            gr.printFile("Std_ReturnType IocReceive_{}({});".format(iocid, iocdataType))
            gr.printFile("Std_ReturnType SysIocReceive_{}({});".format(iocid, iocdataType))
    else:
        gr.printFile("Std_ReturnType IocReceive_{}({}*);".format(iocid, iocdataType)) #改動：拿掉 receiverID
        gr.printFile("Std_ReturnType SysIocReceive_{}({}*);".format(iocid, iocdataType)) #改動：拿掉 receiverID
    gr.printFile("Std_ReturnType IocEmptyQueue_{}(void);".format(iocid))
    gr.printFile("Std_ReturnType SysIocEmptyQueue_{}(void);\n".format(iocid))

def IocWriteGroup_IocReadGroup_and_related_Syscall(ioc, iocid, iocsenders, iocreceivers, iocDataProperties):
    send_datatype = ""
    receiver_datatype = ""
    for iocData in iocDataProperties:
        iocdataType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocData ,"OsIocDataTypeRef")
        if ("*" in iocdataType) and not(iocdataType.endswith("*")): #type ref, uint16 length
            ioctype_ptr = iocdataType.split(",")
            send_datatype += ioctype_ptr[0] + ", uint16"
            receiver_datatype += ioctype_ptr[0] + ", uint16*"
        else:
            send_datatype += iocdataType
            receiver_datatype += iocdataType
            if not("*" in iocdataType):
                receiver_datatype += "*"
        if iocData != iocDataProperties[-1]:
            send_datatype += ", "
            receiver_datatype += ", "
    for sender in iocsenders:
        gr.printFile("Std_ReturnType IocWriteGroup_{}_{}({});".format(iocid, sender, send_datatype))
        gr.printFile("Std_ReturnType SysIocWriteGroup_{}_{}({});".format(iocid, sender, send_datatype))
    for receiver in iocreceivers:
        gr.printFile("Std_ReturnType IocReadGroup_{}_{}({});".format(iocid, receiver, receiver_datatype))
        gr.printFile("Std_ReturnType SysIocReadGroup_{}_{}({});".format(iocid, receiver, receiver_datatype))
    gr.printFile("\n")

def IocWrite_IocRead_and_related_Syscall(ioc, iocid, iocsenders, iocreceivers):
    iocDataProperty = config.getValue("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocDataProperties")
    iocdataType = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocDataProperty ,"OsIocDataTypeRef")

    for sender in iocsenders: #改動：調整整段 IocSend 生成判斷。
        if "*" in iocdataType:
            if "," in iocdataType: #改動
                ioctype_ptr = iocdataType.split(",")
                gr.printFile("Std_ReturnType IocWrite_{}_{}({},uint16);".format(iocid, sender, ioctype_ptr[0]))
                gr.printFile("Std_ReturnType SysIocWrite_{}_{}({},uint16);".format(iocid, sender, ioctype_ptr[0]))
            else:
                gr.printFile("Std_ReturnType IocWrite_{}_{}({});".format(iocid, sender, iocdataType))
                gr.printFile("Std_ReturnType SysIocWrite_{}_{}({});".format(iocid, sender, iocdataType))
        else:
            gr.printFile("Std_ReturnType IocWrite_{}_{}({});".format(iocid, sender, iocdataType))
            gr.printFile("Std_ReturnType SysIocWrite_{}_{}({});".format(iocid, sender, iocdataType))
    
    for receiver in iocreceivers:
        #IocReceive only support N:1 (one receiver)
        if "*" in iocdataType:
            if "," in iocdataType: #type ref, uint16 length
                ioctype_ptr = iocdataType.split(",")
                gr.printFile("Std_ReturnType IocRead_{}_{}({},uint16*);".format(iocid, receiver, ioctype_ptr[0]))
                gr.printFile("Std_ReturnType SysIocRead_{}_{}({},uint16*);".format(iocid, receiver, ioctype_ptr[0]))
            else: #type ref
                gr.printFile("Std_ReturnType IocRead_{}_{}({});".format(iocid, receiver, iocdataType))
                gr.printFile("Std_ReturnType SysIocRead_{}_{}({});".format(iocid, receiver, iocdataType))
        else:
            gr.printFile("Std_ReturnType IocRead_{}_{}({}*);".format(iocid, receiver, iocdataType))
            gr.printFile("Std_ReturnType SysIocRead_{}_{}({}*);".format(iocid, receiver, iocdataType))
        gr.printFile("\n")

def functions_declarations_and_related_extern_types(ioc, iocids):
    gr.printFile("Std_ReturnType IOC_API(int id, void* input_data,int flag);")
    gr.printFile("Std_ReturnType SetCallbackfunctionAction(ApplicationType ,void (*callback)(void));")
    gr.printFile("void memcpy_j(int iocid, void *data, int size, int flag);\n")
    for iocid in iocids: 
        length = config.getValue("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocBufferLength")
        iocDataProperties = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocDataProperties")
        iocsenders = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocSenderProperties")
        iocreceivers = config.getList("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocReceiverProperties")
        #判斷 semantic
        if length != False:
            gr.printFile("\nextern uint16 lock_{} ;".format(iocid))    
            gr.printFile("extern uint8 buffer_{}[{}];".format(iocid, length))
            count = config.getCount("/AUTOSAR/" + ioc + "/" + iocid ,"OsIocReceiverProperties")
            gr.printFile("extern ReceiverType receiver_{}[{}] ;".format(iocid, count))     
            #判斷是否為 group
            if len(iocDataProperties) > 1:
                IocSendGroup_IocReceiveGroup_IocEmptyQueue_and_related_Syscall(ioc, iocid, iocsenders, iocreceivers, iocDataProperties)
            elif len(iocDataProperties) == 1:
                IocSend_IocReceive_IocEmptyQueue_and_related_Syscall(ioc, iocid, iocsenders)
        else:
            if len(iocDataProperties) > 1:
                IocWriteGroup_IocReadGroup_and_related_Syscall(ioc, iocid, iocsenders, iocreceivers, iocDataProperties)
            elif len(iocDataProperties) == 1:
                IocWrite_IocRead_and_related_Syscall(ioc, iocid, iocsenders, iocreceivers)

        #根據 OsIocReceiverPullCB 有無設置，判斷是否生成 callback function
        for iocReceiver in iocreceivers:
            name = config.getValue("/AUTOSAR/" + ioc + "/" + iocid + "/" + iocReceiver ,"OsIocReceiverPullCB")
            if name != False:
                gr.printFile("void callback_{}_{}(void);".format(iocid, name))   


def main():
    gr.genfile = open("../kernel/Ioc.h",'w')

    gr.printFile("#ifndef IOC_H")
    gr.printFile("#define IOC_H")
    
    gr.printFile("/* the generated configuration of ioc */")
    
    #inclusions
    gr.printFile("/*==================[inclusions]=============================================*/")
    gr.printFile("#include \"typedefine.h\"")
    gr.printFile("//#include \"Rte_Type.h\"")
    
    #macros, typedef, and structs
    gr.printFile("/*==================[macros]=================================================*/")
    ioc = config.getValue("/AUTOSAR","OsIoc")
    if ioc != False:
        iocids = config.getList("/AUTOSAR/" + ioc,"OsIocCommunication")
        sender_receiver_and_empty_macros(ioc, iocids)
        ReceiverType_and_IOCCB_struct()
        
        gr.printFile("#define POP 0")
        gr.printFile("#define PUSH 1")

        iocid_count_and_iocid_macros(iocids)

        gr.printFile("/*mask*/")
        gr.printFile("extern IocAutosarType Ioc_channel_sender[IOCID_COUNT];")
        gr.printFile("extern IocAutosarType Ioc_channel_receiver[IOCID_COUNT];")

        struct_for_IOC_api(ioc, iocids)
        gr.printFile("extern IOCCB icb[IOCID_COUNT];\n")

        functions_declarations_and_related_extern_types(ioc, iocids)
    gr.printFile("#endif")

if __name__ == "__main__":
    main()
