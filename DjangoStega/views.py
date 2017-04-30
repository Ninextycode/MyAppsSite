from django.shortcuts import render, redirect
from django.http import HttpResponse
from tempfile import NamedTemporaryFile
from stega_w import Stegacrypto

import os, shutil
# Create your views here.


st_cr = Stegacrypto()

def encoderedirect(request):
    return redirect('encode')


def encodeview(request):
    if(request.method == "POST"):
        noContainerFile = (request.FILES.get("containerFile", None) is None) and request.POST.getlist('method')[0] != "plaincrypto"
        noKeyFile = request.FILES.get("keyFile", None) is None
        noSecretFile = request.FILES.get("secretFile", None) is None
        if (noSecretFile or noKeyFile or noContainerFile):
            return render(request, 'encode.html', context= {
                "noKeyFile" : noKeyFile ,
                "noSecretFile": noSecretFile,
                "noContainerFile": noContainerFile
            })
        container_file = None
        if request.POST.getlist('method')[0] != "plaincrypto":
            container_file = NamedTemporaryFile(suffix=os.path.splitext(request.FILES["containerFile"].name)[1])
            container_file.write(request.FILES["containerFile"].read())
        secret_file = NamedTemporaryFile(suffix="|"+request.FILES["secretFile"].name)
        secret_file.write(request.FILES["secretFile"].read())
        key = request.FILES["keyFile"].read()

        if request.POST.getlist('method')[0] == "plaincrypto":
            st_cr.encrypt_file(secret_file.name, key, "/tmp/")
            result_file = secret_file.name + "_crypt.dat"
            response = HttpResponse(open(result_file, mode="rb").read(), content_type='application/force-download')
            response['Content-Disposition'] = "attachment; filename=" + \
                                              os.path.splitext(request.FILES["secretFile"].name)[0] + \
                                              "_crypt.dat"
            print(os.path.exists(result_file))
            if os.path.exists(result_file):
                os.remove(result_file)
            return response

        elif request.POST.getlist('method')[0] == "jpegstega":
            st_cr.encode_and_hide_file_in_jpeg(password=key, container=container_file.name,
                                                 file=secret_file.name, output_dir="/tmp/")
            container_file.seek(0)
            response = HttpResponse(container_file.read(), content_type='application/force-download')
            response['Content-Disposition'] = "attachment; filename=" + \
                                              request.FILES["containerFile"].name

            return response

        elif request.POST.getlist('method')[0] == "loslessstega":
            st_cr.encode_and_hide_file_in_bmppng(password=key, container=container_file.name,
                                                 file=secret_file.name,  output_dir="/tmp/")
            container_file.seek(0)
            response = HttpResponse(container_file.read(), content_type='application/force-download')
            response['Content-Disposition'] = "attachment; filename=" + \
                                              request.FILES["containerFile"].name

            return response


        secret_file.close()
        container_file.close()

    return render(request, 'encode.html')


def decodeview(request):
    if(request.method == "POST"):
        noContainerFile = request.FILES.get("containerFile", None) is None
        noKeyFile = request.FILES.get("keyFile", None) is None

        if (noKeyFile or noContainerFile):
            return render(request, 'encode.html', context= {
                "noKeyFile" : noKeyFile,
                "noContainerFile": noContainerFile
            })

        container_file = NamedTemporaryFile()
        container_file.write(request.FILES["containerFile"].read())

        key = request.FILES["keyFile"].read()
        output_dir = container_file.name + "_out/"
        os.mkdir(output_dir)
        try:
            if request.POST.getlist('method')[0] == "plaincrypto":
                st_cr.decrypt_file(file=container_file.name, password=key, output_dir=output_dir)
            elif request.POST.getlist('method')[0] == "jpegstega":
                st_cr.decode_and_take_file_from_jpeg(password=key, container=container_file.name,
                                                     output_dir=output_dir)
            elif request.POST.getlist('method')[0] == "loslessstega":
                st_cr.decode_and_take_file_from_bmppng(password=key, imagename=container_file.name,
                                                     output_dir=output_dir)
        except Exception as e:
            print(e)
            shutil.rmtree(output_dir, ignore_errors=True)
            return render(request, 'decode.html', context={"probablyWrongKey":True})

        response = HttpResponse(open(output_dir + os.listdir(output_dir)[0], mode="rb").read(),
                                content_type='application/force-download')
        response['Content-Disposition'] = "attachment; filename=" + \
                                          os.listdir(output_dir)[0][os.listdir(output_dir)[0].find("|")+1:]
        shutil.rmtree(output_dir, ignore_errors=True)

        container_file.close()

        return response



    return render(request, 'decode.html')

