# files_transfer_project

สแกนหาไฟล์วิดีโอในโฟลเดอร์ บันทึกรายการลง JSON แล้วแปลงเป็น MP4 ด้วย ffmpeg
โดยเก็บสถานะของแต่ละไฟล์ไว้ใน JSON ทำให้หยุดแล้วรันต่อได้

## สิ่งที่ต้องมี

- Python 3.8+
- [ffmpeg](https://ffmpeg.org/) อยู่ใน `PATH`
- ถ้าใช้ codec `h264_nvenc` (ค่าเริ่มต้น) ต้องมีการ์ดจอ NVIDIA; ถ้าไม่มีให้ใช้ `-c libx264`

## วิธีใช้

### 1. สแกนไฟล์

```bash
python main.py G:/ -o F:/files_transfer_project/file_details.json -t ts -l 5
```

| option | ความหมาย |
| --- | --- |
| `directory_path` | โฟลเดอร์ที่จะสแกน (รวมโฟลเดอร์ย่อย) |
| `-o, --output-json` | ไฟล์ JSON ที่จะบันทึก (ค่าเริ่มต้น `file_details.json`) |
| `-t, --file-type` | เก็บเฉพาะนามสกุลนี้ เช่น `ts` |
| `-l, --limit` | จำนวนไฟล์สูงสุด |

รันซ้ำได้: ไฟล์ที่มีอยู่ใน JSON แล้วจะไม่ถูกเพิ่มซ้ำ และสถานะเดิมจะไม่ถูกรีเซ็ต

### 2. แปลงเป็น MP4

```bash
python convert_video.py -j F:/files_transfer_project/file_details.json -o F:/files_transfer_project/output_video -f ts -l 20
```

| option | ความหมาย |
| --- | --- |
| `-j, --json-file` | ไฟล์ JSON จากขั้นตอนที่ 1 |
| `-o, --output-path` | โฟลเดอร์ปลายทางของไฟล์ MP4 |
| `-l, --limit` | จำนวนวิดีโอสูงสุดที่จะแปลงในรอบนี้ |
| `-f, --file-filter` | แปลงเฉพาะนามสกุลนี้ (ค่าเริ่มต้น: ทุกไฟล์ที่ไม่ใช่ mp4) |
| `-c, --codec` | `h264_nvenc` (GPU, ค่าเริ่มต้น) หรือ `libx264` (CPU) |
| `--retry-failed` | ลองแปลงไฟล์ที่เคยล้มเหลวอีกครั้ง |

`transfer_status` ของแต่ละไฟล์จะเป็น `none`, `success` หรือ `failed` และถูกบันทึกลง JSON
หลังแปลงเสร็จแต่ละไฟล์ ไฟล์ที่ชื่อซ้ำกัน (อยู่คนละโฟลเดอร์) จะถูกตั้งชื่อ output เป็น `ชื่อ_ลำดับ.mp4`
เพื่อไม่ให้ทับกัน

## ทดสอบ

```bash
python -m unittest -v
```
