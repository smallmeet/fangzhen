import os


class Sha256Digest:

    # Initialise the SHA256 computation
    def __init__(self):
        self.ihash = []
        self.count = [0, 0]
        self.buffer = [0] * 64
        self.ihash.append(1779033703)
        self.ihash.append(3144134277)
        self.ihash.append(1013904242)
        self.ihash.append(1359893119)
        self.ihash.append(2773480762)
        self.ihash.append(2600822924)
        self.ihash.append(528734635)
        self.ihash.append(1541459225)

        self.sha256_hex_digits = "0123456789abcdef"
        self.K256 = [
            1116352408, 1899447441, 3049323471, 3921009573, 961987163,
            1508970993, 2453635748, 2870763221, 3624381080, 310598401,
            607225278, 1426881987, 1925078388, 2162078206, 2614888103,
            3248222580, 3835390401, 4022224774, 264347078, 604807628,
            770255983, 1249150122, 1555081692, 1996064986, 2554220882,
            2821834349, 2952996808, 3210313671, 3336571891, 3584528711,
            113926993, 338241895, 666307205, 773529912, 1294757372,
            1396182291, 1695183700, 1986661051, 2177026350, 2456956037,
            2730485921, 2820302411, 3259730800, 3345764771, 3516065817,
            3600352804, 4094571909, 275423344, 430227734, 506948616,
            659060556, 883997877, 958139571, 1322822218, 1537002063,
            1747873779, 1955562222, 2024104815, 2227730452, 2361852424,
            2428436474, 2756734187, 3204031479, 3329325298,
        ]

    def rotateRight(self, b, a):
        return (a >> b) | (a << (32 - b))

    def choice(self, a, c, b):
        return (a & c) ^ (~a & b)

    def majority(self, a, c, b):
        return (a & c) ^ (a & b) ^ (c & b)

    def sha256_Sigma0(self, a):
        return self.rotateRight(2, a) ^ self.rotateRight(13, a) ^ self.rotateRight(22, a)

    def sha256_Sigma1(self, a):
        return self.rotateRight(6, a) ^ self.rotateRight(11, a) ^ self.rotateRight(25, a)

    def sha256_sigma0(self, a):
        return self.rotateRight(7, a) ^ self.rotateRight(18, a) ^ (a >> 3)

    def sha256_sigma1(self, a):
        return self.rotateRight(17, a) ^ self.rotateRight(19, a) ^ (a >> 10)

    def sha256_expand(self, a, b):
        a[b & 15] += self.sha256_sigma1(a[(b + 14) & 15]) + a[(b + 9) & 15] + self.sha256_sigma0(a[(b + 1) & 15])
        return a[b & 15]

    def fileSlice(self, b, d, c):
        a = c + d
        if b.slice:
            return b.slice(d, a)
        else:
            if b.mozSlice:
                return b.mozSlice(d, a)
            else:
                if b.webkitSlice:
                    return b.webkitSlice(d, a)

    def safe_add(self, a, d):
        c = (a & 65535) + (d & 65535)
        b = (a >> 16) + (d >> 16) + (c >> 16)
        return (b << 16) | (c & 65535)

    def sha256_transform(self):
        k = [0] * 16
        w = self.ihash[0]
        v = self.ihash[1]
        u = self.ihash[2]
        t = self.ihash[3]
        r = self.ihash[4]
        p = self.ihash[5]
        o = self.ihash[6]
        n = self.ihash[7]
        for m in range(16):
            k[m] = ((self.buffer[(m << 2) + 3]) | (self.buffer[(m << 2) + 2] << 8) | (self.buffer[(m << 2) + 1] << 16) | (self.buffer[m << 2] << 24))
        for l in range(16):
            s = n + self.sha256_Sigma1(r) + self.choice(r, p, o) + self.K256[l]
            if l < 16:
                s += k[l]
            else:
                s += self.sha256_expand(k, l)
            q = self.sha256_Sigma0(w) + self.majority(w, v, u)
            n = o
            o = p
            p = r
            r = self.safe_add(t, s)
            t = u
            u = v
            v = w
            w = self.safe_add(s, q)
        self.ihash[0] += w
        self.ihash[1] += v
        self.ihash[2] += u
        self.ihash[3] += t
        self.ihash[4] += r
        self.ihash[5] += p
        self.ihash[6] += o
        self.ihash[7] += n

    # Read the next chunk of data and update the SHA256 computation
    def sha256_update(self, f, d):
        g = 0
        b = ((self.count[0] >> 3) & 63)
        e = (d & 63)
        self.count[0] += (d << 3)
        if self.count[0] < (d << 3):
            self.count[1] += 1
        self.count[1] += (d >> 29)
        c = 63
        while c < d:
            a = b
            while a < 64:
                self.buffer[a] = ord(f[g])
                g += 1
                a += 1
            self.sha256_transform()
            b = 0
            c += 64
        for i in range(e):
            self.buffer[i] = f[g]  # ord(f[g])
            g += 1

    def sha256_final(self):
        a = (self.count[0] >> 3) & 63
        self.buffer[a] = 128
        if a <= 56:
            b = a
            while b < 56:
                self.buffer[b] = 0
                b += 1
        else:
            b = a
            while b < 64:
                self.buffer[b] = 0
                b += 1
            self.sha256_transform()
            for b in range(56):
                self.buffer[b] = 0
        self.buffer[56] = (self.count[1] >> 24) & 255
        self.buffer[57] = (self.count[1] >> 16) & 255
        self.buffer[58] = (self.count[1] >> 8) & 255
        self.buffer[59] = self.count[1] & 255
        self.buffer[60] = (self.count[0] >> 24) & 255
        self.buffer[61] = (self.count[0] >> 16) & 255
        self.buffer[62] = (self.count[0] >> 8) & 255
        self.buffer[63] = self.count[0] & 255
        self.sha256_transform()

    def sha256_encode_bytes(self):
        b = 0
        a = [0] * 32
        for c in range(8):
            a[b] = (self.ihash[c] >> 24) & 255
            b += 1
            a[b] = (self.ihash[c] >> 16) & 255
            b += 1
            a[b] = (self.ihash[c] >> 8) & 255
            b += 1
            a[b] = self.ihash[c] & 255
            b += 1
        return a

    def sha256_encode_hex(self):
        a = ""
        for c in range(8):
            b = 28
            while b >= 0:
                a += self.sha256_hex_digits.charAt((self.ihash[c] >> b) & 15)
                b -= 4
        return a

    # Main function: returns a hex string representing the SHA256 value of the given data
    def sha256_digest(self):
        with open(r'D:\apk\58dd447a48bd672fa963754cd1bdde34.apk', 'rb') as f:
            i = 0
            file_size = os.path.getsize(r'D:\apk\58dd447a48bd672fa963754cd1bdde34.apk')
            print(file_size)
            while i < file_size:
                content = str(f.read(1024 * 1024), encoding='ISO-8859-1')
                self.sha256_update(content, len(content))
                i += 1024 * 1024
                f.seek(i)
        print('yyyy')
        self.sha256_final()
        return self.sha256_encode_hex()


def main():
    sha_256 = Sha256Digest()
    print(sha_256.sha256_digest())


if __name__ == '__main__':
    main()