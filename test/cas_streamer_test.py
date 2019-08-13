from controller.cas_streamer import CasEntryStreamer


streamer = CasEntryStreamer()
flags = {'basic': False, 'ird': False, 'simple': False, 'file': True}
streamer.setup_streamer('C:/Users/WitLab-DaeHwan/Desktop/tmp',
                        'http://210.102.142.14:4000/api/nl/witlab/cas/',
                        flags)
streamer.streaming_on()


