# Buildroot Bootloader Setup Guide

To use the `genimage.cfg` and `grub.cfg` provided, configure Buildroot as follows:

## 1. `make menuconfig`

**Bootloaders**
*   [x] **grub2**
*   [x]   **i386-pc** (For Legacy BIOS)
*   [x]   **x86-64-efi** (For UEFI)
*   [x]   **Install tools** (Optional, useful for debugging)
*   [ ]   **Builtin modules**: `boot linux ext2 fat part_gpt part_msdos normal efi_gop` (Add these space-separated)

**Kernel**
*   [x] **Install kernel image to /boot in target**: `no` (We load from rootfs or boot partition, standard is fine)
*   Ensure `CONFIG_EFI_STUB=y` in kernel config.

## 2. Post-Image Script (`board/synapta/post-image.sh`)

You must create a script to organize the files for `genimage`. Buildroot generates `grub.img` and `grubx64.efi` flat in `images/`. `genimage` (vfat) needs them in a directory structure.

```bash
#!/bin/bash
# Move files for genimage
BOARD_DIR="$(dirname $0)"
GENIMAGE_CFG="${BOARD_DIR}/genimage.cfg"
GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"

# 1. Prepare EFI folder structure
mkdir -p ${BINARIES_DIR}/efi-part/EFI/BOOT

# 2. Copy UEFI Bootloader
cp ${BINARIES_DIR}/grubx64.efi ${BINARIES_DIR}/efi-part/EFI/BOOT/bootx64.efi

# 3. Copy Config
cp ${BOARD_DIR}/grub.cfg ${BINARIES_DIR}/grub.cfg

# 4. Call Genimage
rm -rf "${GENIMAGE_TMP}"
genimage \
  --rootpath "${TARGET_DIR}" \
  --tmppath "${GENIMAGE_TMP}" \
  --inputpath "${BINARIES_DIR}" \
  --outputpath "${BINARIES_DIR}" \
  --config "${GENIMAGE_CFG}"

echo "Image generated at ${BINARIES_DIR}/synapta-os.img"
```

## 3. Integration
Set `BR2_ROOTFS_POST_IMAGE_SCRIPT` to `board/synapta/post-image.sh` in your config.
