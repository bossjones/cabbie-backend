# host setting
TCP_IP = '127.0.0.1'
TCP_PORT = 5005
TCP_ADDR = (TCP_IP, TCP_PORT)

# skb G/W host setting
SKBGW_HOST = ('180.64.233.242', '180.64.233.243')

# internal api server host setting
APISERVER_HOST = ('127.0.0.1', '54.168.6.134', '176.34.2.86')

BUFFER_SIZE = 1024  # Normally 1024, but we want fast response
        
# for login
USERNAME='threeline'
PASSWORD='security'

# DES encryption key
DES_CBC_ENCRYPTION_KEY1 = 'fedcba9876543210'
DES_CBC_ENCRYPTION_KEY2 = 'f1e0d3c2b5a49786'
DES_CBC_ENCRYPTION_KEY3 = '0129456789abcdef'
DES_CBC_ENCRYPTION_KEY = DES_CBC_ENCRYPTION_KEY1 + DES_CBC_ENCRYPTION_KEY2 + DES_CBC_ENCRYPTION_KEY3
DES_CBC_IV = 'ffddbaa876543211'

# message header
HEADER_BYTE_LENGTH = 24

HEADER_MSG_ID_FOR_REQUEST   = '11000128'
HEADER_MSG_ID_FOR_RESPONSE  = '12000128'
HEADER_SRC_ID               = '00000d00'
HEADER_DEST_ID              = '00000001'
HEADER_GROUP_ID             = '00010000'
HEADER_MSG_SEQUENCE_NO      = '00000000'

HEADER_REQUEST = '{msg_id}{src_id}{dest_id}{group_id}{msg_seq_no}'.format(
                    msg_id = HEADER_MSG_ID_FOR_REQUEST,
                    src_id = HEADER_SRC_ID,
                    dest_id = HEADER_DEST_ID,
                    group_id = HEADER_GROUP_ID,
                    msg_seq_no = HEADER_MSG_SEQUENCE_NO 
                )

HEADER_RESPONSE = '{msg_id}{src_id}{dest_id}{group_id}{msg_seq_no}'.format(
                    msg_id = HEADER_MSG_ID_FOR_RESPONSE,
                    src_id = HEADER_SRC_ID,
                    dest_id = HEADER_DEST_ID,
                    group_id = HEADER_GROUP_ID,
                    msg_seq_no = HEADER_MSG_SEQUENCE_NO 
                )



SECRET_KEY = 'dd8ab4f01f15088ccd63c3498246aea7c195ac87'
