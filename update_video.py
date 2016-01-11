#!/bin/python

import os

from shutil import copyfile
from sqlalchemy import create_engine
from converter import Converter


class FileStorage(object):

    def __init__(self, file, filename):
        self.file = file
        self.filename = filename


def _get_path(media_name):
    return '/opt/Axitube/data/media/%s' % media_name


def transcode(media_file, template_file):
        """
        Transcode the video into three videos with predefined
        dimensions and predefined formats.
        """
        vid_formats = [
        ]

        if media_file.unique_id.endswith('webm'):
            vid_formats.append(('webm', 'vp8', 'vorbis'))

        if media_file.unique_id.endswith('mp4'):
            vid_formats.append(('mp4', 'h264', 'aac'))

        vid_size = []

        if media_file.quality == '240':
            vid_size.append(
                {'width': 426, 'height': 240, 'name': '240',}
            )
        if media_file.quality == '360':
            vid_size.append(
                {'width': 640, 'height': 360, 'name': '360',},
            )
        if media_file.quality == '480':
            vid_size.append(
                {'width': 854, 'height': 480, 'name': '480',},
            )
        if media_file.quality == '720':
            vid_size.append(
                {'width': 1280, 'height': 720, 'name': '720',},
            )
        if media_file.quality == '1080':
            vid_size.append(
                {'width': 1920, 'height': 1080, 'name': '1080',},
            )

        c = Converter()
        file_path = _get_path(media_file.unique_id)
        template_file_path = _get_path(template_file.unique_id)
        info = c.probe(template_file_path)

        copyfile(file_path, _get_path('cp/%s' % media_file.unique_id))

        nb_transcoded_files = 0
        for vs in vid_size:
            if vs['name'] != 'sd' and vs['height'] > info.video.video_height and vs['width'] > info.video.video_width:
                nb_transcoded_files += 1
                continue
            ratio = float(vs['height']) / info.video.video_height
            vw = int(info.video.video_width*ratio)
            if vw % 2:
                vw += 1
            for vf in vid_formats:
                fname, ext = os.path.splitext(template_file_path)
                to_file_name = '%s_%s_%s.%s' % (
                    fname,
                    vs['width'],
                    vs['height'],
                    vf[0],
                )
                opts = {
                    'threads': 1,
                    'format': vf[0],
                    'audio': {
                        'codec': vf[2],
                    },
                    'video': {
                        'src_width': info.video.video_width,
                        'src_height': info.video.video_height,
                        'codec': vf[1],
                        'width': vw,
                        'height': vs['height'],
                        'mode': 'stretch',
                    },
                }

                conv = c.convert(
                     template_file_path,
                     to_file_name,
                     opts,
                     timeout=None,
                 )
                complete_percentage = (nb_transcoded_files / 1.00)
                for timecode in conv:
                    print media_file.unique_id, int(((timecode / 100.00 / 1.00) + complete_percentage) * 100)
                nb_transcoded_files += 1

                info_out = c.probe(to_file_name)
                fstore = FileStorage(os.fdopen(os.open(to_file_name, os.O_RDONLY)), to_file_name)

if __name__ == '__main__':
    engine = create_engine('mysql://docker:axitube@localhost/axitube?charset=utf8&use_unicode=0')
    conn = engine.connect()
    result = conn.execute('SELECT * FROM media_files WHERE template = 1;')
    for template in result:
        template_name = '%s%%' % template.unique_id.split('.')[0]
        all_files = conn.execute('SELECT * FROM media_files WHERE unique_id LIKE %s AND template = 0', template_name)
        for af in all_files:
            transcode(af, template)