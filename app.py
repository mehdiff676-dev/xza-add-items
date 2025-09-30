#━━━━━━━━━━━━━━━━━━━
# 𝗠𝗔𝗗𝗘 𝗕𝗬 𝗙𝗢𝗫 x 𝗟7𝗔𝗝
# 𝗣𝗥𝗢𝗝𝗘𝗖𝗧𝗦 𝗙𝗢𝗫𝗫
# 𝗠𝗬 𝗨𝗦𝗘𝗥 : @illllillilllli
#━━━━━━━━━━━━━━━━━━━

from flask import Flask, request, jsonify
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
import requests

app = Flask(__name__)

#━━━━━━━━━━━━━━━━━━━
# ProtoBuf
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6, 30, 0, '', 'data.proto'
)
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\ndata.proto"7\n\x12InnerNestedMessage\x12\x0f\n\x07\x66ield_6\x18\x06 \x01(\x03\x12\x10\n\x08\x66ield_14\x18\x0e \x01(\x03"\x87\x01\n\nNestedItem\x12\x0f\n\x07\x66ield_1\x18\x01 \x01(\x05\x12\x0f\n\x07\x66ield_2\x18\x02 \x01(\x05\x12\x0f\n\x07\x66ield_3\x18\x03 \x01(\x05\x12\x0f\n\x07\x66ield_4\x18\x04 \x01(\x05\x12\x0f\n\x07\x66ield_5\x18\x05 \x01(\x05\x12$\n\x07\x66ield_6\x18\x06 \x01(\x0b\x32\x13.InnerNestedMessage"@\n\x0fNestedContainer\x12\x0f\n\x07\x66ield_1\x18\x01 \x01(\x05\x12\x1c\n\x07\x66ield_2\x18\x02 \x03(\x0b\x32\x0b.NestedItem"A\n\x0bMainMessage\x12\x0f\n\x07\x66ield_1\x18\x01 \x01(\x05\x12!\n\x07\x66ield_2\x18\x02 \x03(\x0b\x32\x10.NestedContainerb\x06proto3'
)
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'data_pb2', _globals)
MainMessage = _globals["MainMessage"]

#━━━━━━━━━━━━━━━━━━━
# Key & IV
key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

#━━━━━━━━━━━━━━━━━━━
@app.route("/send_item", methods=["GET", "POST"])
def send_item():
    try:
        if request.method == "POST":
            data_req = request.get_json()
            item_id = data_req.get("item_id")
            jwt_token = data_req.get("jwt_token")
        else:  # GET
            item_id = request.args.get("item_id")
            jwt_token = request.args.get("jwt_token")

        if not item_id or not jwt_token:
            return jsonify({"error": "يرجى إدخال item_id و jwt_token"}), 400

        # Build protobuf
        data = MainMessage()
        data.field_1 = 1
        container1 = data.field_2.add()
        container1.field_1 = 1

        item = container1.field_2.add()
        item.field_1 = 2
        item.field_4 = 1
        item.field_6.field_6 = int(item_id)

        # Serialize + Encrypt
        data_bytes = data.SerializeToString()
        padded_data = pad(data_bytes, AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(padded_data)

        # Request
        url = "https://clientbp.ggblueshark.com/SetPlayerGalleryShowInfo"
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": "OB50",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Dalvik/2.1.0 (Linux; Android 11)",
            "Host": "clientbp.ggblueshark.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }

        response = requests.post(url, headers=headers, data=encrypted_data)

        return jsonify({
            "status": response.status_code,
            "response": response.text
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#━━━━━━━━━━━━━━━━━━━
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)