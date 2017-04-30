import stega
import struct
from PIL import Image
import numpy as np
import scipy.misc
import os
from shutil import copyfile, move


#wrapper for stega library to provide support for autocompletion


class Stegacrypto:
    def __init__(self):
        self.stegaworker = stega.Stega()
        self.cryptoworker = stega.Crypto()

    def hide_file_in_bmppng(self, file, imagename):
        self.create_temp_from_image(imagename)
        self.stegaworker.hide_file_in_temp(file)
        self.create_image_from_temp(imagename)
        os.remove(self.stegaworker.temp_filename)

    def take_file_from_bmppng(self, imagename, output_dir):
        self.create_temp_from_image(imagename)
        self.stegaworker.take_file_from_temp(output_dir)
        os.remove(self.stegaworker.temp_filename)

    def create_temp_from_image(self, imagename):
        im = Image.open(imagename)
        if im.format != "PNG" and im.format != "BMP":
            raise Exception("Wrong image format " + im.format)

        if im.mode != "RGB":
            im = im.convert("RGBA")

        data = np.asarray(im)

        alpha = False
        if data.shape[2] == 4:
            alpha = True

        with open(self.stegaworker.temp_filename, "wb") as f:
            f.write(struct.pack('>I', data.shape[0]))
            f.write(struct.pack('>I', data.shape[1]))
            for r in range(data.shape[0]):
                for c in range(data.shape[1]):
                    for k in range(3):
                        f.write(struct.pack("B", data[r][c][k]))
            if alpha:
                for r in range(data.shape[0]):
                    for c in range(data.shape[1]):
                        f.write(struct.pack("B", data[r][c][3]))

    def create_image_from_temp(self, imagename):
        bytes = open(self.stegaworker.temp_filename, "rb").read()
        width = struct.unpack(">I", bytes[0:4])[0]
        height = struct.unpack(">I", bytes[4:8])[0]

        rgbsize = width * height * 3
        argbsize = width * height * 4
        bodysize = len(bytes) - 8
        if rgbsize == bodysize:
            data = self.create_image_from_bytes_rgb(bytes)
        elif argbsize == bodysize:
            data = self.create_image_from_bytes_rgba(bytes)
        else:
            raise Exception("Problems with temp file." +
                            " Size is " + str(bodysize)+ ", but " + str(argbsize) + " or " + str(rgbsize) + " expected")
        scipy.misc.imsave(imagename, data)

    def create_image_from_bytes_rgb(self, bytes):
        width = struct.unpack(">I", bytes[0:4])[0]
        height = struct.unpack(">I", bytes[4:8])[0]

        index = 8
        data = np.zeros(shape = (width, height, 3))
        for r in range(data.shape[0]):
            for c in range(data.shape[1]):
                for k in range(3):
                    data[r][c][k] = bytes[index]
                    index += 1
        return data

    def create_image_from_bytes_rgba(self, bytes):
        width = struct.unpack(">I", bytes[0:4])[0]
        height = struct.unpack(">I", bytes[4:8])[0]

        index = 8
        data = np.zeros(shape = (width, height, 4))
        for r in range(data.shape[0]):
            for c in range(data.shape[1]):
                for k in range(3):
                    data[r][c][k] = bytes[index]
                    index += 1
        for r in range(data.shape[0]):
            for c in range(data.shape[1]):
                data[r][c][3] = bytes[index]
                index += 1
        return data

    def hide_file_in_jpeg(self, file, container):
        self.stegaworker.hide_file_in_jpeg(file, container)

    def take_file_from_jpeg(self, container, output_dir):
        self.stegaworker.take_file_from_jpeg(container, output_dir)

    def clean_jpeg(self, container):
        self.stegaworker.clean_jpeg(container)

    def encode_and_hide_file_in_bmppng(self, password, container, file, output_dir):
        try:
            self.unsafe_encode_and_hide_file_in_bmppng(password, container, file, output_dir)
        finally:
            if os.path.exists(self.stegaworker.temp_filename):
                os.remove(self.stegaworker.temp_filename)

    def unsafe_encode_and_hide_file_in_bmppng(self, password, container, file, output_dir):
        container = self.create_new_container(container, output_dir)
        self.create_temp_from_image(container)
        try:
            self.stegaworker.encode_and_hide_file_in_temp(password, file)
        except Exception as e:
            if os.path.exists(container):
                os.remove(container)
            raise e
        self.create_image_from_temp(container)

    def decode_and_take_file_from_bmppng(self, password, imagename, output_dir):
        try:
            self.create_temp_from_image(imagename)
            self.stegaworker.decode_and_take_file_from_temp(password, output_dir)
        finally:
            if os.path.exists(self.stegaworker.temp_filename):
                os.remove(self.stegaworker.temp_filename)

    def encode_and_hide_file_in_jpeg(self, password, file, container, output_dir):
        container = self.create_new_container(container, output_dir)
        try:
            self.stegaworker.encode_and_hide_file_in_jpeg(password, file, container)
        except Exception as e:
            if os.path.exists(container):
                os.remove(container)

    def decode_and_take_file_from_jpeg(self, password, container, output_dir):
        self.stegaworker.decode_and_take_file_from_jpeg(password, container, output_dir)

    def create_new_container(self, container, output_dir):
        filename = os.path.basename(container)

        new_container_path = os.path.join(output_dir, filename)

        if not os.path.exists(new_container_path):
            copyfile(container, new_container_path)
        elif not os.path.samefile(container, new_container_path):
            os.remove(new_container_path)
            copyfile(container, new_container_path)

        return new_container_path

    def encrypt_file(self, file, password, output_dir):
        self.cryptoworker.encrypt_file(file, password, output_dir)

    def decrypt_file(self, file, password, output_dir):
        self.cryptoworker.decrypt_file(file, password, output_dir)
