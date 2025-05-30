# Secure Spam Protected P2P Chat Application

This project is a Peer-to-Peer (P2P) messaging platform that enables secure, encrypted communication between devices connected over a LAN (Local Area Network) without using the internet. It includes:

- 💬 Real-time peer-to-peer messaging
- 🔒 DES-based encryption from scratch
- 🚫 Spam message detection using machine learning


## 📡 How It Works

1. One device starts the server using `main.py`.
2. Other peers connect using the server's IP and port.
3. Messages are:
   - Checked for spam
   - Encrypted using DES
   - Sent to connected peers
   - Decrypted on the receiving end

