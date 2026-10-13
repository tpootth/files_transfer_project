import os
import subprocess
import tempfile
import unittest
from unittest import mock

from convert_video import process_videos
from module.list_files import list_files
from module.save_to_json import load_json, save_to_json, write_json


def touch(path, size=0):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(b'x' * size)


class ListFilesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        touch(os.path.join(self.root, 'a.ts'), 10)
        touch(os.path.join(self.root, 'b.TS'))
        touch(os.path.join(self.root, 'c.mp4'))
        touch(os.path.join(self.root, 'sub', 'd.ts'))

    def tearDown(self):
        self.tmp.cleanup()

    def test_filter_by_type_is_case_insensitive(self):
        names = [f['file_name'] for f in list_files(self.root, '.TS')]
        self.assertEqual(names, ['a.ts', 'b.TS', 'd.ts'])

    def test_limit(self):
        files = list_files(self.root, 'ts', '2')
        self.assertEqual([f['number'] for f in files], [1, 2])

    def test_empty_limit_and_type_mean_all(self):
        self.assertEqual(len(list_files(self.root, '', '')), 4)


class SaveToJsonTest(unittest.TestCase):
    def test_merge_does_not_duplicate_or_reset_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'out.json')
            item = {'number': 1, 'file_path': '/x/a.ts', 'transfer_status': 'none'}
            self.assertEqual(save_to_json([dict(item)], path), 1)

            data = load_json(path)
            data[0]['transfer_status'] = 'success'
            write_json(data, path)

            new = {'number': 1, 'file_path': '/x/b.ts', 'transfer_status': 'none'}
            self.assertEqual(save_to_json([dict(item), new], path), 1)
            data = load_json(path)
            self.assertEqual([d['file_path'] for d in data], ['/x/a.ts', '/x/b.ts'])
            self.assertEqual([d['number'] for d in data], [1, 2])
            self.assertEqual(data[0]['transfer_status'], 'success')


class ProcessVideosTest(unittest.TestCase):
    def test_converts_pending_and_records_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            touch(os.path.join(tmp, 'in', 'one', 'clip.ts'))
            touch(os.path.join(tmp, 'in', 'two', 'clip.ts'))
            touch(os.path.join(tmp, 'in', 'bad.ts'))
            json_path = os.path.join(tmp, 'files.json')
            save_to_json(list_files(os.path.join(tmp, 'in')), json_path)
            out = os.path.join(tmp, 'out')

            def fake_convert(input_path, output_file, codec):
                if input_path.endswith('bad.ts'):
                    return False
                touch(output_file)
                return True

            with mock.patch('convert_video.convert_to_mp4', side_effect=fake_convert) as conv:
                self.assertEqual(process_videos(json_path, out), (2, 1))
                self.assertEqual(conv.call_count, 3)

            data = {os.path.basename(os.path.dirname(d['file_path'])) + '/' + d['file_name']: d
                    for d in load_json(json_path)}
            self.assertEqual(data['in/bad.ts']['transfer_status'], 'failed')
            outputs = sorted(os.path.basename(d['output_path']) for d in data.values() if d['output_path'])
            self.assertEqual(len(outputs), 2)
            self.assertNotEqual(outputs[0], outputs[1])

            with mock.patch('convert_video.convert_to_mp4', side_effect=fake_convert) as conv:
                self.assertEqual(process_videos(json_path, out), (0, 0))
                process_videos(json_path, out, retry_failed=True)
                self.assertEqual(conv.call_count, 1)

    def test_default_skips_non_video_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ('a.ts', 'b.MKV', 'c.mp4', 'notes.txt', 'photo.jpg'):
                touch(os.path.join(tmp, 'in', name))
            json_path = os.path.join(tmp, 'files.json')
            save_to_json(list_files(os.path.join(tmp, 'in')), json_path)

            with mock.patch('convert_video.convert_to_mp4', return_value=True) as conv:
                process_videos(json_path, os.path.join(tmp, 'out'))
            converted = sorted(os.path.basename(c.args[0]) for c in conv.call_args_list)
            self.assertEqual(converted, ['a.ts', 'b.MKV'])


class ConvertToMp4Test(unittest.TestCase):
    def test_ctrl_c_removes_part_file(self):
        from module.convert_to_mp4 import convert_to_mp4
        with tempfile.TemporaryDirectory() as tmp:
            dst = os.path.join(tmp, 'clip.mp4')
            part = os.path.join(tmp, 'clip.part.mp4')

            def interrupted_ffmpeg(*args, **kwargs):
                touch(part)
                raise KeyboardInterrupt

            with mock.patch('module.convert_to_mp4.subprocess.run', side_effect=interrupted_ffmpeg):
                with self.assertRaises(KeyboardInterrupt):
                    convert_to_mp4('in.ts', dst)
            self.assertFalse(os.path.exists(part))
            self.assertFalse(os.path.exists(dst))


@unittest.skipUnless(subprocess.run(['which', 'ffmpeg'], capture_output=True).returncode == 0,
                     'ffmpeg not installed')
class FfmpegTest(unittest.TestCase):
    def test_real_conversion_with_libx264(self):
        from module.convert_to_mp4 import convert_to_mp4
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, 'src.ts')
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc=duration=1:size=64x64',
                            '-f', 'lavfi', '-i', 'sine=duration=1', '-c:v', 'mpeg2video', '-c:a', 'mp2', src],
                           check=True)
            dst = os.path.join(tmp, 'out', 'src.mp4')
            self.assertTrue(convert_to_mp4(src, dst, 'libx264'))
            self.assertTrue(os.path.getsize(dst) > 0)
            self.assertFalse(os.path.exists(os.path.join(tmp, 'out', 'src.part.mp4')))
            self.assertFalse(convert_to_mp4(os.path.join(tmp, 'missing.ts'), dst + '2.mp4', 'libx264'))


if __name__ == '__main__':
    unittest.main()
