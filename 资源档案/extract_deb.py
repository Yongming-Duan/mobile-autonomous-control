#!/usr/bin/env python3
"""Extract deb package without ar command"""

import struct
import os
import tarfile
import sys

def extract_deb(deb_path, output_dir='.'):
    """Extract a deb package"""

    with open(deb_path, 'rb') as f:
        # Check ar magic number
        magic = f.read(8)
        if magic != b'!<arch>\n':
            print("Error: Not a valid ar archive")
            return False

        print(f"Extracting {deb_path}...")

        while True:
            # Read file header (60 bytes)
            header = f.read(60)
            if not header or len(header) < 60:
                break

            # Parse header
            name = header[:16].decode('ascii').strip()
            timestamp = struct.unpack('>I', header[16:20])[0]
            owner_id = struct.unpack('>I', header[20:24])[0]
            group_id = struct.unpack('>I', header[24:28])[0]
            mode = struct.unpack('>I', header[28:32])[0]
            size = struct.unpack('>I', header[48:52])[0]

            # Skip padding
            if f.read(2) != b'\x60\x0a':
                print("Warning: Invalid padding")

            if not name:
                break

            print(f"  File: {name} ({size} bytes)")

            # Read file data
            data = f.read(size)

            # Pad to even boundary
            if size % 2 != 0:
                f.read(1)

            # Extract data.tar or control.tar
            if name.startswith('data.tar') or name.startswith('control.tar'):
                # Determine compression type
                if name.endswith('.xz'):
                    import lzma
                    try:
                        tar_data = lzma.decompress(data)
                    except:
                        # Try external command
                        import subprocess
                        result = subprocess.run(['unxz', '-c', '-'], input=data, capture_output=True)
                        if result.returncode == 0:
                            tar_data = result.stdout
                        else:
                            print(f"    Failed to decompress {name}")
                            continue
                elif name.endswith('.gz'):
                    import gzip
                    tar_data = gzip.decompress(data)
                else:
                    tar_data = data

                # Extract tar archive
                import io
                with tarfile.open(fileobj=io.BytesIO(tar_data)) as tar:
                    tar.extractall(path=output_dir)
                    print(f"    Extracted to {output_dir}/")
                continue

            # Save other files
            output_path = os.path.join(output_dir, name)
            with open(output_path, 'wb') as out:
                out.write(data)

    print("Extraction complete!")
    return True

if __name__ == '__main__':
    deb_path = sys.argv[1] if len(sys.argv) > 1 else '../termux-api_0.59.1-1_aarch64.deb'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
    extract_deb(deb_path, output_dir)
