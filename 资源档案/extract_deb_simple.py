#!/usr/bin/env python3
import os
import sys
import struct

def extract_deb_simple(deb_file, extract_to='.'):
    """Simple AR archive extractor for deb files"""

    with open(deb_file, 'rb') as f:
        # Check magic
        magic = f.read(8)
        if magic != b'!<arch>\n':
            print("Not an AR archive")
            return

        os.makedirs(extract_to, exist_ok=True)

        while True:
            # Read 60 byte header
            header = f.read(60)
            if len(header) < 60:
                break

            # Parse header (fixed format in AR)
            # Name: 16 bytes (right-padded with spaces)
            name_bytes = header[:16]
            try:
                name = name_bytes.decode('ascii').rstrip(' /')
            except:
                break

            if not name:
                continue

            # Timestamp: 12 bytes
            # Owner ID: 6 bytes
            # Group ID: 6 bytes
            # Mode: 8 bytes
            # Size: 10 bytes
            size_bytes = header[48:58]
            try:
                size = int(size_bytes.decode('ascii').strip())
            except:
                break

            # End marker: 2 bytes ("\`60\n")
            f.read(2)

            print(f"Found: {name} ({size} bytes)")

            # Read content
            content = f.read(size)

            # Write to file
            clean_name = name.rstrip('/')
            output_file = os.path.join(extract_to, clean_name)

            if name.startswith('data.tar') or name.startswith('control.tar'):
                # Write tar file
                with open(output_file, 'wb') as out:
                    out.write(content)

                # Now extract the tar
                if clean_name.endswith('.xz'):
                    try:
                        import lzma
                        tar_content = lzma.decompress(content)
                        # Extract tar
                        import tarfile
                        import io
                        with tarfile.open(fileobj=io.BytesIO(tar_content)) as tar:
                            tar.extractall(path=extract_to)
                        print(f"  Extracted {clean_name}")
                    except Exception as e:
                        print(f"  Error: {e}")
                elif clean_name.endswith('.gz'):
                    try:
                        import gzip
                        tar_content = gzip.decompress(content)
                        import tarfile
                        import io
                        with tarfile.open(fileobj=io.BytesIO(tar_content)) as tar:
                            tar.extractall(path=extract_to)
                        print(f"  Extracted {clean_name}")
                    except Exception as e:
                        print(f"  Error: {e}")
                else:
                    # No compression
                    import tarfile
                    with tarfile.open(output_file) as tar:
                        tar.extractall(path=extract_to)
                    print(f"  Extracted {clean_name}")
            else:
                # Save as-is
                with open(output_file, 'wb') as out:
                    out.write(content)

            # Pad to even byte boundary
            if size % 2 == 1:
                f.read(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: extract_deb_simple.py <deb-file> [output-dir]")
        sys.exit(1)

    deb_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '.'

    extract_deb_simple(deb_file, output_dir)
