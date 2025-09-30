#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
from flask import Flask, request, jsonify
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
app = Flask(__name__)

# نسخة اللعبة
freefire_version = "OB50"

# المفتاح و iv
key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ProtoBuf Descriptor
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6, 30, 0, '', 'data.proto'
)
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\ndata.proto\"7\n\x12InnerNestedMessage\x12\x0f\n\x07\x66ield_6\x18\x06 \x01(\x03\x12\x10\n\x08\x66ield_14\x18\x0e \x01(\x03\"\x87\x01\n\nNestedItem\x12\x0f\n\x07\x66ield_1\x18\x01 \x01(\x05\x12\x0f\n\x07\x66ield_2\x18\x02 \x01(\x05\x12\x0f\n\x07\x66ield_3\x18\x03 \x01(\x05\x12\x0f\n\x07\x66ield_4\x18\x04 \x01(\x05\x12\x0f\n\x07\x66ield_5\x18\x05\x12$\n\x07\x66ield_6\x18\x06 \x01(\x0b\x32\x13.InnerNestedMessage\"@\n\x0fNestedContainer\x12\x0f\n\x07\x66ield_1\x18\x01 \x01(\x05\x12\x1c\n\x07\x66ield_2\x18\x02 \x03(\x0b\x32\x0b.NestedItem\"A\n\x0bMainMessage\x12\x0f\n\x07\x66ield_1\x18\x01 \x01(\x05\x12!\n\x07\x66ield_2\x18\x02 \x03(\x0b\x32\x10.NestedContainerb\x06proto3'
)
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'data_pb2', _globals)

MainMessage = _globals["MainMessage"]

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@app.route("/send_items", methods=["POST"])
def send_items():
    try:
        # Step 1: استلام البيانات من المستخدم
        data = request.get_json()
        access = data.get("access")
        item_ids = data.get("item_ids")  # ← لائحة IDs
        if not access or not item_ids:
            return jsonify({"error": "الرجاء إدخال access و item_ids"}), 400

        if not isinstance(item_ids, list):
            return jsonify({"error": "item_ids يجب أن تكون List"}), 400

        # Step 2: تحويل access → JWT
        jwt_api_url = f"https://projects-fox-x-get.vercel.app/api/{access}"
        jwt_response = requests.get(jwt_api_url)

        if jwt_response.status_code != 200:
            return jsonify({"error": "فشل في تحويل access إلى JWT"}), 400

        jwt_token = jwt_response.text.strip()

        # Step 3: تكوين البيانات
        msg = MainMessage()
        msg.field_1 = 1
        container1 = msg.field_2.add()
        container1.field_1 = 1

        for item_id in item_ids:
            item = container1.field_2.add()
            item.field_1 = 2
            item.field_4 = 1
            item.field_6.field_6 = int(item_id)

        # Serialize + Encrypt
        data_bytes = msg.SerializeToString()
        padded_data = pad(data_bytes, AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(padded_data)

        #━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Step 4: إرسال الطلب
        url = "https://clientbp.ggblueshark.com/SetPlayerGalleryShowInfo"
        headers = {
            "Expect": "100-continue",
            "Authorization": f"Bearer {jwt_token}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": freefire_version,
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-A305F Build/RP1A.200720.012)",
            "Host": "clientbp.ggblueshark.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }

        response = requests.post(url, headers=headers, data=encrypted_data)

        if response.status_code == 200:
            return jsonify({
                "status": "success",
                "msg": f"تم إرسال {len(item_ids)} عنصر/عناصر بنجاح",
                "items": item_ids,
                "code": response.status_code
            })
        else:
            return jsonify({
                "status": "error",
                "code": response.status_code,
                "text": response.text
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)