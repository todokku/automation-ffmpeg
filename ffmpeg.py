import os
import shutil


def correct_ass_timeline(fn):
    with open(fn, 'r') as f:
        previous_ts = None
        result = list()

        line = f.readline()
        while line:
            if 'Dialogue' not in line:
                result.append(line)
            else:
                segs = line.split(',')
                ts1 = segs[1]
                ts2 = segs[2]
                if not previous_ts:
                    previous_ts = ts2
                    result.append(line)
                else:
                    if ts1 <= previous_ts:
                        min_ts = min(previous_ts, ts1)
                        _, milsec = min_ts.split('.')
                        milsec = "%02d" % (
                            int(milsec) + 3 if int(milsec) + 3 <= 99 else 99)
                        min_ts_add = '.'.join([_, milsec])

                        _previous_line = result.pop().split(',')
                        _previous_line[2] = min_ts
                        result.append(','.join(_previous_line))

                        _line = line.split(',')
                        _line[1] = min_ts_add
                        result.append(','.join(_line))

                        previous_ts = ts2
                    else:
                        previous_ts = ts2
                        result.append(line)

            line = f.readline()

    with open(fn, 'w') as f:
        f.write(('').join(result))


vids_base = os.getcwd()
for channel in os.listdir(vids_base):
    channel_path = os.path.join(vids_base, channel)
    if os.path.isdir(channel_path):
        # get all videos extension mp4
        vids_list = list()
        for item in os.listdir(channel_path):
            item_path = os.path.join(channel_path, item)
            if '.mp4' in item:
                vids_list.append(
                    (item[:-4], os.path.join(channel_path, item[:-4]), item_path))
        # create coressponding directory
        for vid_name, vid_dir, vid_path in vids_list:
            thumnail = vid_dir + '.jpg'
            zh_vtt = vid_dir + '.zh-Hans.vtt'
            en_vtt = vid_dir + '.en.vtt'
            zh_ass = vid_dir + '.zh-Hans.ass'

            # convert vtt to ass
            if os.path.exists(zh_vtt):
                if not os.path.exists(vid_dir):
                    os.mkdir(vid_dir)

                print('converting %s..' % zh_vtt)
                os.system('ffmpeg -i "%s" "%s" -y' % (zh_vtt, zh_ass))

                # fix ass timeline issue
                if zh_ass.endswith('.ass'):
                    correct_ass_timeline(zh_ass)

                output = "[PROCESSED]" + vid_name + ".mp4"
                # ffmpeg to 'burns the subtitles' into the video
                os.system('ffmpeg -i "%s" -vf "subtitles=%s" "%s" -y' %
                          (vid_path, zh_ass, os.path.join(vid_dir, output)))

                # copy thumbnail to final output folder
                if os.path.exists(thumnail):
                    _copied_path = shutil.copy(thumnail, vid_dir)
