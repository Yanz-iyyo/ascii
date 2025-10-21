import subprocess
import sys

def install_package(package):
    """Menginstal package menggunakan pip."""
    try:
        print(f"Mencoba menginstal {package}...")
        subprocess.run([sys.executable, "-m", "pip", "install", package], check=True, capture_output=True, text=True)
        print(f"{package} berhasil diinstal.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Gagal menginstal {package}. Error: {e.stderr}")
        return False

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Library 'Pillow' tidak ditemukan.")
    if install_package("Pillow"):
        print("Silakan jalankan kembali skripnya.")
        sys.exit(0)
    else:
        print("Program tidak dapat melanjutkan tanpa Pillow.")
        sys.exit(1)

# Daftar karakter ASCII berdasarkan tingkat kecerahan
ASCII_SETS = {
    "detail": ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."],
    "sederhana": ["#", "-", " "],
    "blok": ["█", "▓", "▒", "░", " "],
}

def get_neofetch_banner(distro="Arch"):
    """Menjalankan neofetch untuk mendapatkan banner ASCII distro."""
    try:
        result = subprocess.run(
            ["neofetch", f"--ascii_distro", distro],
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("=" * 50)
        print("Peringatan: Perintah 'neofetch' tidak ditemukan.")
        print("Pastikan neofetch terinstal: 'pkg install neofetch'")
        print("=" * 50)
    except Exception as e:
        print(f"Terjadi kesalahan saat menjalankan neofetch: {e}")

def resize_image(image, new_width=100):
    """Mengubah ukuran gambar dengan mempertahankan rasio aspek."""
    width, height = image.size
    ratio = height / width / 1.65
    new_height = int(new_width * ratio)
    return image.resize((new_width, new_height))

def image_to_ascii(image, ascii_chars):
    """Mengonversi gambar menjadi daftar karakter ASCII dan warnanya."""
    rgb_image = image.convert("RGB")
    pixels = list(rgb_image.getdata())
    ascii_data = []
    for r, g, b in pixels:
        pixel_value = (r + g + b) / 3
        index = min(int(pixel_value / 256 * len(ascii_chars)), len(ascii_chars) - 1)
        ascii_char = ascii_chars[index]
        ascii_data.append((ascii_char, (r, g, b)))
    return ascii_data

def add_text_to_image(image, text, position="center", size=20, color=(255, 255, 255)):
    """Menambahkan teks kustom ke gambar dengan berbagai opsi."""
    draw = ImageDraw.Draw(image)

    # Coba gunakan font Arial, jika tidak ada, gunakan font default
    try:
        font = ImageFont.truetype("arial.ttf", size)
    except IOError:
        print("Peringatan: Font 'arial.ttf' tidak ditemukan, menggunakan font default.")
        # Untuk Pillow versi baru, load_default() mungkin tidak punya argumen size
        # Jadi kita coba cara lain atau biarkan default sepenuhnya
        try:
            font = ImageFont.load_default(size=size)
        except TypeError:
            font = ImageFont.load_default()

    # Dapatkan ukuran gambar dan teks untuk penentuan posisi
    img_width, img_height = image.size

    # Gunakan textbbox untuk mendapatkan bounding box yang akurat (Pillow >= 9.2.0)
    try:
        text_box = draw.textbbox((0, 0), text, font=font)
        text_width = text_box[2] - text_box[0]
        text_height = text_box[3] - text_box[1]
    except AttributeError:
        # Fallback untuk versi Pillow yang lebih lama
        text_width, text_height = draw.textsize(text, font=font)

    # Kalkulasi posisi x, y berdasarkan input string
    margin = 10
    positions = {
        "top-left": (margin, margin),
        "top-center": ((img_width - text_width) / 2, margin),
        "top-right": (img_width - text_width - margin, margin),
        "center-left": (margin, (img_height - text_height) / 2),
        "center": ((img_width - text_width) / 2, (img_height - text_height) / 2),
        "center-right": (img_width - text_width - margin, (img_height - text_height) / 2),
        "bottom-left": (margin, img_height - text_height - margin),
        "bottom-center": ((img_width - text_width) / 2, img_height - text_height - margin),
        "bottom-right": (img_width - text_width - margin, img_height - text_height - margin),
    }

    if position not in positions:
        print("Peringatan: Posisi tidak dikenali, menggunakan posisi 'center'.")
        position = "center"

    x, y = positions[position]

    draw.text((x, y), text, font=font, fill=color)
    return image

def display_ascii_art(ascii_data, width, use_color=False):
    """Mencetak ASCII art ke konsol, dengan atau tanpa warna."""
    reset_color = "\033[0m"

    # Gabungkan seluruh output ke dalam satu string untuk dicetak sekali
    # Ini jauh lebih cepat daripada memanggil print() untuk setiap karakter
    output_buffer = []
    for i, (char, (r, g, b)) in enumerate(ascii_data):
        if use_color:
            # Gunakan ANSI escape code untuk warna 24-bit
            color_code = f"\033[38;2;{r};{g};{b}m"
            output_buffer.append(color_code + char)
        else:
            output_buffer.append(char)

        if (i + 1) % width == 0:
            # Reset warna di akhir baris dan tambah baris baru
            output_buffer.append(reset_color + "\n")

    print("".join(output_buffer))

def format_for_file(ascii_data, width):
    """Memformat ASCII art sebagai string teks biasa untuk disimpan ke file."""
    output_lines = []
    line = []
    for i, (char, color) in enumerate(ascii_data):
        line.append(char)
        if (i + 1) % width == 0:
            output_lines.append("".join(line))
            line = []
    # Jika ada sisa karakter di baris terakhir
    if line:
        output_lines.append("".join(line))
    return "\n".join(output_lines)


def display_menu():
    """Menampilkan menu interaktif."""
    print("\n" + "=" * 50)
    print(" " * 15 + "ASCII Art Generator")
    print("=" * 50)
    print("1. Buat ASCII Art dari Gambar")
    print("2. Tampilkan Banner Neofetch")
    print("3. Keluar")
    print("=" * 50)
    return input("Pilih opsi (1-3): ")

def main():
    """Fungsi utama untuk menjalankan generator ASCII."""
    while True:
        choice = display_menu()

        if choice == "1":
            image_path = input("Masukkan path ke gambar: ")
            try:
                image = Image.open(image_path)
            except FileNotFoundError:
                print(f"Error: File tidak ditemukan di '{image_path}'")
                continue
            except Exception as e:
                print(f"Error: Tidak dapat membuka gambar. {e}")
                continue

            # Opsi kustomisasi
            width = int(input("Masukkan lebar ASCII art (contoh: 100): ") or 100)
            print("Pilih set karakter ASCII:")
            for i, (key, value) in enumerate(ASCII_SETS.items()):
                print(f"{i+1}. {key} ({''.join(value)})")
            char_choice = input(f"Pilih set (1-{len(ASCII_SETS)}): ")
            char_keys = list(ASCII_SETS.keys())
            selected_chars = ASCII_SETS[char_keys[int(char_choice)-1]] if char_choice.isdigit() and 1 <= int(char_choice) <= len(ASCII_SETS) else ASCII_SETS["detail"]

            color_choice = input("Gunakan warna? (y/n): ").lower()
            use_color = color_choice == 'y'

            # Opsi Teks Kustom
            add_text_choice = input("Tambahkan teks kustom di atas gambar? (y/n): ").lower()
            if add_text_choice == 'y':
                custom_text = input("Masukkan teks: ")
                if custom_text:
                    print("Pilih posisi teks (contoh: center, top-left, bottom-right)")
                    position = input("Posisi [default: center]: ") or "center"

                    try:
                        size_input = input("Masukkan ukuran font [default: 20]: ")
                        size = int(size_input) if size_input else 20
                    except ValueError:
                        print("Ukuran tidak valid, menggunakan default (20).")
                        size = 20

                    try:
                        color_str = input("Masukkan warna font R,G,B [default: 255,255,255]: ") or "255,255,255"
                        color = tuple(map(int, color_str.split(',')))
                        if len(color) != 3:
                            raise ValueError
                    except (ValueError, TypeError):
                        print("Format warna tidak valid, menggunakan putih (255,255,255).")
                        color = (255, 255, 255)

                    image = add_text_to_image(image, custom_text, position=position, size=size, color=color)


            resized_image = resize_image(image, new_width=width)
            ascii_art = image_to_ascii(resized_image, selected_chars)

            # Tampilkan ASCII art di konsol menggunakan fungsi baru
            img_width = resized_image.width
            display_ascii_art(ascii_art, img_width, use_color)

            # Simpan ke file menggunakan fungsi pemformatan baru
            save_choice = input("Simpan ASCII art ke file? (y/n): ").lower()
            if save_choice == 'y':
                file_name = input("Masukkan nama file (contoh: ascii_art.txt): ")
                with open(file_name, "w") as f:
                    f.write(format_for_file(ascii_art, img_width))
                print(f"ASCII art disimpan ke {file_name}")


        elif choice == "2":
            distro = input("Masukkan nama distro (contoh: Arch, Ubuntu, Fedora) atau biarkan kosong: ")
            get_neofetch_banner(distro if distro else "Arch")

        elif choice == "3":
            print("Terima kasih telah menggunakan ASCII Art Generator!")
            break

        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nKeluar dari program.")
