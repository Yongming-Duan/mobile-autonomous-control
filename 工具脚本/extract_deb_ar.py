#!/usr/bin/env python3
"""
AR archive extractor for Debian packages
Works without needing the 'ar' command
"""

import os
import sys
import struct
import tarfile
import lzma
import gzip

def extract_ar_archive(ar_file, extract_to='.'):
    """Extract AR archive (like .deb files)"""

    print(f"Extracting {ar_file} to {extract_to}...")

    with open(ar_file, 'rb') as f:
        # Check AR magic
        magic = f.read(8)
        if magic != b'!<arch>\n':
            print(f"Error: Not a valid AR archive")
            return False

        os.makedirs(extract_to, exist_ok=True)

        file_count = 0

        while True:
            # Read file header
            header = f.read(60)
            if len(header) < 60:
                break

            # Parse AR header (fixed format)
            # Name: 16 bytes, right padded with spaces
            # Timestamp: 12 bytes
            # Owner ID: 6 bytes
            # Group ID: 6 bytes
            # Mode: 8 bytes
            # Size: 10 bytes
            # End marker: 2 bytes

            name = header[:16].decode('ascii').strip()
            timestamp = header[16:28].decode('ascii').strip()
            owner_id = header[28:34].decode('ascii').strip()
            group_id = header[34:40].decode('ascii').strip()
            mode = header[40:48].decode('ascii').strip()
            size = int(header[48:58].decode('ascii').strip())

            # Read end marker
            end_marker = f.read(2)
            if end_marker != b'\x60\x0a':
                # Some AR archives use different end marker
                f.seek(-2, 1)

            if not name or name == '//':  # Skip special entries
                if size > 0:
                    f.read(size)
                    if size % 2 == 1:
                        f.read(1)
                continue

            print(f"  Extracting: {name} ({size} bytes)")

            # Read file data
            data = f.read(size)

            # Pad to even byte boundary
            if size % 2 == 1:
                f.read(1)

            # Save file
            clean_name = name.rstrip('/')
            output_path = os.path.join(extract_to, clean_name)

            # Handle special GNU long filename format
            if name.startswith('#1/'):
                # GNU long filename format
                long_name_len = int(name[3:])
                long_name = data[:long_name_len].decode('ascii')
                file_data = data[long_name_len:]
                output_path = os.path.join(extract_dir, long_name)
                with open(output_path, 'wb') as out:
                    out.write(file_data)
            elif name.startswith('data.tar') or name.startswith('control.tar'):
                # Extract tar archive
                try:
                    # Save tar file first
                    tar_path = os.path.join(extract_to, clean_name)
                    with open(tar_path, 'wb') as out:
                        out.write(data)

                    # Decompress and extract
                    if clean_name.endswith('.xz'):
                        tar_content = lzma.decompress(data)
                        with tarfile.open(fileobj=__import__('io').BytesIO(tar_content)) as tar:
                            tar.extractall(path=extract_to)
                        print(f"    -> Extracted to {extract_to}/")
                    elif clean_name.endswith('.gz'):
                        tar_content = gzip.decompress(data)
                        with tarfile.open(fileobj=__import__('io').BytesIO(tar_content)) as tar:
                            tar.extractall(path=extract_to)
                        print(f"    -> Extracted to {extract_to}/")
                    else:
                        # No compression
                        with tarfile.open(tar_path) as tar:
                            tar.extractall(path=extract_to)
                        print(f"    -> Extracted to {extract_to}/")

                    file_count += 1
                except Exception as e:
                    print(f"    -> Error extracting: {e}")
            else:
                # Save as regular file
                with open(output_path, 'wb') as out:
                    out.write(data)
                file_count += 1

    print(f"\nExtraction complete! {file_count} files extracted.")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: extract_deb_ar.py <ar-file> [output-dir]")
        print("\nExample:")
        print("  extract_deb_ar.py package.deb extracted/")
        sys.exit(1)

    ar_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'extracted'

    extract_ar_archive(ar_file, output_dir)
