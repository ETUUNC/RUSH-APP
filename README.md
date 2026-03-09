# RUSH - Üye Yönetim Sistemi

Flask tabanlı üye kayıt ve admin yönetim sistemi.

## Kurulum ve Çalıştırma

### 1. Gereksinimler
- Python 3.8+
- pip (Python paket yöneticisi)

### 2. Sanal Ortam Oluşturma ve Bağımlılıkları Yükleme

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Veritabanı Oluşturma

Uygulama ilk çalıştırmada otomatik olarak `rush.db` dosyasını oluşturur. Manuel oluşturmak isterseniz:

```powershell
python create_rush_db.py
```

### 4. Uygulamayı Başlatma

```powershell
python app.py
```

Tarayıcınızda açın: http://127.0.0.1:5000/

---

## Uygulama Kullanımı

### Kullanıcı Tarafı

#### Üye Kaydı
1. Ana sayfada **"Kayıt Ol"** butonuna tıklayın
2. Formu doldurun:
   - Ad Soyad
   - E-Posta
   - Telefon
3. **"Kaydet"** butonuna tıklayın
4. Kayıt başarılı olur ve admin onayı beklenir

### Admin Paneli

#### Admin Girişi
1. Ana sayfada **"Admin Girişi"** butonuna tıklayın veya `/login` adresine gidin
2. Giriş bilgileri:
   - **Kullanıcı Adı:** `leroleroo`
   - **Parola:** `TUNÇ3031`
3. **"Giriş"** butonuna tıklayın

#### Admin Panel Özellikleri

Admin panelinde 3 ana bölüm bulunur:

##### 1. Bekleyen Kayıtlar
Kullanıcıların yaptığı kayıtlar burada görünür.
- **Onayla:** Üyeyi kayıtlı üyeler kısmına taşır
- **Reddet:** Üyeyi reddedilenler kısmına taşır

##### 2. Kayıtlı Üyeler
Onaylanmış üyeler bu bölümde listelenir.
- **Düzenle:** Üye bilgilerini düzenle (telefon, ödeme durumu, ödeme tarihi)
- **Ödendi Yap:** Ödeme durumunu hızlıca "Ödendi" olarak işaretle
- **Sil:** Üyeyi tamamen sil (geri alınamaz)

##### 3. Reddedilen Kayıtlar
Reddedilen üyeler burada görünür.
- **Geri Al:** Üyeyi tekrar "Bekleyen Kayıtlar" bölümüne taşı
- **Sil:** Üyeyi tamamen sil

#### Üye Ekleme (Admin)
Admin, kullanıcı kaydı beklemeden direk üye ekleyebilir:

1. Admin panelinde **"Üye Ekle"** butonuna tıklayın
2. Formu doldurun:
   - Ad Soyad
   - E-Posta
   - Telefon
3. **"Kaydet"** butonuna tıklayın
4. Üye **otomatik olarak onaylanmış** şekilde "Kayıtlı Üyeler" bölümüne eklenir

#### Üye Düzenleme
1. Kayıtlı üyeler listesinde ilgili üyenin yanındaki **"Düzenle"** linkine tıklayın
2. Düzenlenebilir alanlar:
   - **Telefon:** Değiştirmek için checkbox'ı işaretleyin
   - **Ödeme Durumu:** Bekliyor, Ödendi, İptal
   - **Ödeme Tarihi:** Tarih ve saat seçin (isteğe bağlı)
3. **"Kaydet"** butonuna tıklayın

> **Not:** Ödeme durumu "Ödendi" seçildiğinde ödeme tarihi boş bırakılırsa, sistem otomatik olarak şu anki tarihi kaydeder.

#### Ödeme Takibi
- Sistem, 30 günden eski kayıtların ödeme durumunu otomatik olarak "Bekliyor" yapar
- Admin girişinde, ödemesi tamamlanmamış üye sayısı bildirim olarak gösterilir
- Ödeme durumları renkli olarak gösterilir:
  - **Yeşil:** Ödendi
  - **Kırmızı:** İptal
  - **Sarı:** Bekliyor

---

## Güvenlik Notları

- **Production için** `RUSH_SECRET_KEY` ortam değişkenini mutlaka ayarlayın
- Admin şifresini değiştirmek için `create_admin.py` veya `insert_admin.py` scriptlerini kullanın
- CSRF koruması aktif

---



## Dosya Yapısı

```
RUSH/
├── app.py                  # Ana Flask uygulaması
├── requirements.txt        # Python bağımlılıkları
├── rush.db                # SQLite veritabanı (otomatik oluşturulur)
├── static/
│   ├── style.css          # CSS stilleri
│   └── images/            # Görseller
└── templates/
    ├── index.html         # Ana sayfa
    ├── register.html      # Kullanıcı kayıt formu
    ├── login.html         # Admin giriş sayfası
    ├── admin.html         # Admin paneli
    ├── admin_add_member.html  # Admin üye ekleme
    └── admin_edit.html    # Admin üye düzenleme
```
