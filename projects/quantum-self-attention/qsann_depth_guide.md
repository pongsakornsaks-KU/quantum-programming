# D_enc และ D_q/k/v คืออะไร

คำตอบสั้นที่สุด: **D คือจำนวนบล็อกวงจรที่ทำซ้ำ** จึงเรียกได้ว่าเป็น
“ความลึกของ quantum circuit” หรือ “จำนวน circuit layers” แต่ไม่ใช่จำนวน
QSAL layers ของ neural network

## ระวังคำว่า layer สองความหมาย

1. **QSAL layer** คือ self-attention หนึ่งชั้นเต็ม ๆ ซึ่งมี `U_enc`, `U_q`,
   `U_k` และ `U_v`
2. **Circuit layer หรือ ansatz layer** คือบล็อก gate เล็ก ๆ ที่ทำซ้ำอยู่ภายใน
   `U_enc`, `U_q`, `U_k` หรือ `U_v`

ค่า D ในเปเปอร์หมายถึงข้อ 2

## D_enc

`D_enc` คือจำนวนรอบของบล็อก encoding `CNOT + RY(data)` ภายใน `U_enc`

```text
H -> RX(data) -> RY(data) -> [ CNOT + RY(data) ] x D_enc
```

หน้าที่ของ `U_enc` คือเอา embedding ของคำใส่เข้าไปใน quantum state
`|psi_s>` มุมของ RX/RY ในส่วนนี้มาจาก embedding จึงไม่ใช่ trainable
parameters

ในโครงสร้างของเปเปอร์:

```text
embedding dimension d = n(D_enc + 2)
```

ดังนั้นเพิ่ม `D_enc` หมายถึง encoder ลึกขึ้น ใช้ gate มากขึ้น และรับค่าใน
embedding ไปเป็นมุมหมุนได้มากขึ้น

## D_q, D_k และ D_v

หลัง encoding แล้ว state เดียวกันจะผ่าน PQC สามตัว:

```text
U_q: RX(theta_q) -> RY(theta_q) -> [ CNOT + RY(theta_q) ] x D_q
U_k: RX(theta_k) -> RY(theta_k) -> [ CNOT + RY(theta_k) ] x D_k
U_v: RX(theta_v) -> RY(theta_v) -> [ CNOT + RY(theta_v) ] x D_v
```

- `D_q` คือจำนวนบล็อกซ้ำในวงจร Query
- `D_k` คือจำนวนบล็อกซ้ำในวงจร Key
- `D_v` คือจำนวนบล็อกซ้ำในวงจร Value

มุม `theta_q`, `theta_k`, `theta_v` เป็น trainable parameters การเพิ่ม D
จึงทำให้วงจรลึกขึ้นและเพิ่มความสามารถในการเรียนรู้ แต่ก็เพิ่มจำนวน gate,
พารามิเตอร์ และเวลาในการคำนวณ

PQC หนึ่งตัวมี trainable parameters:

```text
n(D + 2)
```

## ตัวอย่างใน demo

```text
n = 2 qubits
D_enc = 1
D_q = D_k = D_v = 1
```

จึงหมายความว่า `U_enc`, `U_q`, `U_k` และ `U_v` ต่างมีบล็อก
`CNOT + RY` ที่ทำซ้ำหนึ่งรอบ ไม่ได้หมายความว่าโมเดลมี QSAL หลายชั้น

สรุปอีกครั้ง:

| ค่า | สิ่งที่นับ | มุมมาจากไหน |
| --- | --- | --- |
| `D_enc` | จำนวนบล็อกซ้ำใน encoder | embedding data |
| `D_q` | จำนวนบล็อกซ้ำใน Query PQC | trainable `theta_q` |
| `D_k` | จำนวนบล็อกซ้ำใน Key PQC | trainable `theta_k` |
| `D_v` | จำนวนบล็อกซ้ำใน Value PQC | trainable `theta_v` |

