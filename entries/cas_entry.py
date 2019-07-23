import datetime
import os

from debugmodule import Log


class CasEntry:
    """
    CAS 140 CT - 152 Spectrometer Measurement Data
    <용어 정리>
    엔트리 (entry) : CAS 1회 측정에 해당하는 광특성 집합, ISD 파일 하나를 의미
    광특성 요소 (Attribute, attrib) : ISD 로 출력되는 모든 값 하나하나 (ex. 조도 : Photometric)
    범주 (category) : element 들의 분류를 위한 데이터 집합, ISD 파일에서 []로 둘러싸여있음
    """

    # categories
    _measurement_conditions = {}
    _results = {}
    _general_information = {}
    _sp_ird = {}
    _uv = {}
    _additionals = {}
    valid = None  # 유효 플래그 (ISD 파일이 올바른 형식이고 mapping이 정상적이면 True)
    objDatetime = None  # 측정 시간 객체, str으로 반환 및 시간연산을 위해 쓰임

    newkeymap = {  # old_name : new_name
        'file_abs_path': 'file_abs_path',
        'file_name': 'file_name',
        'IntegrationTime': 'integration_time',
        'CCDTemperature': 'ccd_temp',
        'DCCCDTemperature': 'dc_ccd_temp',
        'Last Dark Current': 'last_dark_current',
        'Signal Level (Counts)': 'signal_level_cnt',
        'Signal Level (%)': 'signal_level_percent',
        'Radiometric': 'bird_all',
        'Photometric': 'illum',
        'UVA': 'cas_uva',
        'UVB': 'cas_uvb',
        'UVC': 'cas_uvc',
        'VIS': 'bird_vis',
        'Tristimulus_X': 'tri_x',
        'Tristimulus_Y': 'tri_y',
        'Tristimulus_Z': 'tri_z',
        'FootLambert': 'foot_lambert',
        'ColorCoordinates/x': 'color_co_x',
        'ColorCoordinates/y': 'color_co_y',
        'ColorCoordinates/z': 'color_co_z',
        'ColorCoordinates/u': 'color_co_u',
        'ColorCoordinates/v1960': 'color_co_v1960',
        'ColorCoordinates/v1976': 'color_co_v1976',
        'PeakWavelength': 'peak_wl',
        'CentroidWavelength': 'cent_wl',
        'DominantWavelength': 'domi_wl',
        'Purity': 'purity',
        'Width50': 'width50',
        'CCT': 'cct',
        'CCT_JIS': 'cct_jis',
        'PlanckDistance': 'planck_dist',
        'SDCM': 'sdcm',
        'RedEffect': 'red_effect',
        'VisEffect': 'vis_effect',
        'CRI': 'cri',
        'CRI/CRI01': 'cri01',
        'CRI/CRI02': 'cri02',
        'CRI/CRI03': 'cri03',
        'CRI/CRI04': 'cri04',
        'CRI/CRI05': 'cri05',
        'CRI/CRI06': 'cri06',
        'CRI/CRI07': 'cri07',
        'CRI/CRI08': 'cri08',
        'CRI/CRI09': 'cri09',
        'CRI/CRI10': 'cri10',
        'CRI/CRI11': 'cri11',
        'CRI/CRI12': 'cri12',
        'CRI/CRI13': 'cri13',
        'CRI/CRI14': 'cri14',
        'CRI/CRI15': 'cri15',
        'CRI/CRI16': 'cri16',
        'CDI': 'cdi',
        'TM30FidelityIndex': 'tm30_fi_idx',
        'TM30FidelityIndex/Rfh01': 'tm30_fi_idx_01',
        'TM30FidelityIndex/Rfh02': 'tm30_fi_idx_02',
        'TM30FidelityIndex/Rfh03': 'tm30_fi_idx_03',
        'TM30FidelityIndex/Rfh04': 'tm30_fi_idx_04',
        'TM30FidelityIndex/Rfh05': 'tm30_fi_idx_05',
        'TM30FidelityIndex/Rfh06': 'tm30_fi_idx_06',
        'TM30FidelityIndex/Rfh07': 'tm30_fi_idx_07',
        'TM30FidelityIndex/Rfh08': 'tm30_fi_idx_08',
        'TM30FidelityIndex/Rfh09': 'tm30_fi_idx_09',
        'TM30FidelityIndex/Rfh10': 'tm30_fi_idx_10',
        'TM30FidelityIndex/Rfh11': 'tm30_fi_idx_11',
        'TM30FidelityIndex/Rfh12': 'tm30_fi_idx_12',
        'TM30FidelityIndex/Rfh13': 'tm30_fi_idx_13',
        'TM30FidelityIndex/Rfh14': 'tm30_fi_idx_14',
        'TM30FidelityIndex/Rfh15': 'tm30_fi_idx_15',
        'TM30FidelityIndex/Rfh16': 'tm30_fi_idx_16',
        'TM30GamutIndex': 'tmp30_gam_idx',
        'TM30GraphicShifts/Chroma01': 'tmp30_grph_ch01',
        'TM30GraphicShifts/Chroma02': 'tmp30_grph_ch02',
        'TM30GraphicShifts/Chroma03': 'tmp30_grph_ch03',
        'TM30GraphicShifts/Chroma04': 'tmp30_grph_ch04',
        'TM30GraphicShifts/Chroma05': 'tmp30_grph_ch05',
        'TM30GraphicShifts/Chroma06': 'tmp30_grph_ch06',
        'TM30GraphicShifts/Chroma07': 'tmp30_grph_ch07',
        'TM30GraphicShifts/Chroma08': 'tmp30_grph_ch08',
        'TM30GraphicShifts/Chroma09': 'tmp30_grph_ch09',
        'TM30GraphicShifts/Chroma10': 'tmp30_grph_ch10',
        'TM30GraphicShifts/Chroma11': 'tmp30_grph_ch11',
        'TM30GraphicShifts/Chroma12': 'tmp30_grph_ch12',
        'TM30GraphicShifts/Chroma13': 'tmp30_grph_ch13',
        'TM30GraphicShifts/Chroma14': 'tmp30_grph_ch14',
        'TM30GraphicShifts/Chroma15': 'tmp30_grph_ch15',
        'TM30GraphicShifts/Chroma16': 'tmp30_grph_ch16',
        'TM30GraphicShifts/Hue01': 'tmp30_grph_hu01',
        'TM30GraphicShifts/Hue02': 'tmp30_grph_hu02',
        'TM30GraphicShifts/Hue03': 'tmp30_grph_hu03',
        'TM30GraphicShifts/Hue04': 'tmp30_grph_hu04',
        'TM30GraphicShifts/Hue05': 'tmp30_grph_hu05',
        'TM30GraphicShifts/Hue06': 'tmp30_grph_hu06',
        'TM30GraphicShifts/Hue07': 'tmp30_grph_hu07',
        'TM30GraphicShifts/Hue08': 'tmp30_grph_hu08',
        'TM30GraphicShifts/Hue09': 'tmp30_grph_hu09',
        'TM30GraphicShifts/Hue10': 'tmp30_grph_hu10',
        'TM30GraphicShifts/Hue11': 'tmp30_grph_hu11',
        'TM30GraphicShifts/Hue12': 'tmp30_grph_hu12',
        'TM30GraphicShifts/Hue13': 'tmp30_grph_hu13',
        'TM30GraphicShifts/Hue14': 'tmp30_grph_hu14',
        'TM30GraphicShifts/Hue15': 'tmp30_grph_hu15',
        'TM30GraphicShifts/Hue16': 'tmp30_grph_hu16',
        'lwr': 'lwr',
        'mwr': 'mwr',
        'swr': 'swr',
        'narr': 'narr',
        'auv': 'auv',
        'duv': 'duv',
        'euv': 'euv',
        'euva': 'euva',
        'euva_ratio': 'euva_ratio',
        'euvb': 'euvb',
        'euvb_ratio': 'euvb_ratio',
        'tuv': 'tuv',
        'uva': 'uva',
        'uvb': 'uvb',
        'uvi': 'uvi',
    }

    def __init__(self, fname: str, debug=False):
        """
        1. ISD 파일 읽기
        2. mapping
        3. ISD 파일 닫기
        4. 파장비율 계산
        5. uv 계산
        6. 측정 시간 객체 생성
        7. 기타 정보 작성 및 수정

        :param fname: ISD 파일의 절대경로, :type: str
        :param debug: ISD parsing debug mode, :type: bool
        """

        # 0. initialize vars
        self.fname = fname
        self.debug = debug
        self.tag = 'CasEntry(%s)' % fname.split('\\')[1]

        # 1. ISD 파일 읽기
        try:
            isdfile = open(fname, 'rt', encoding='utf-8', errors='ignore')
        except (FileNotFoundError, PermissionError) as e:
            if self.debug:
                Log.e(self.tag + '.__init__()', 'file read error: ', e.__class__.__name__)
            self.valid = False
            return

        # 2. mapping
        self.valid = self._map_data(isdfile)

        # 3. ISD 파일 닫기
        isdfile.close()

        if self.valid:
            # 4. 파장비율 계산
            self._set_wl_ratio(alg='trapezoid')

            # 5. uv 계산
            self._set_uv_ird(alg='trapezoid')

            # 6. 측정 시간 객체 생성
            try:
                self.objDatetime = datetime.datetime.strptime(
                    self._general_information['Date'] + ' ' + self._general_information['Time'],
                    '%m/%d/%Y %I:%M:%S %p')
            except (ValueError, TypeError, Exception):
                if self.debug:
                    Log.e(self.tag + '.__init__()', 'error reading datetime: ',
                          self._general_information['Date'] + ' ' + self._general_information['Time'])
                self.objDatetime = None

            # 7. 기타 정보 작성
            self.set_additional_data()

        else:  # not valid entry
            if self.debug:
                Log.e(self.tag + '.__init__()', 'mapping error: ISD file is not correct.')

    def _map_data(self, file):
        """
        ISD 파일을 읽고 element를 category 별 dictionary에 mapping함
        :param file: ISD 파일 객체
        :return: ISD 파일이 정상적인지, mapping 중 오류는 없었는지 여부, :type: boolean
        """
        line = file.readline()
        category = 0

        if line.strip() != '[Curve Information]':
            if self.debug:
                Log.e(self.tag + '._map_data()', 'There is no line [Curve Information]')
            return False

        while line:
            line = line.strip()
            if line == '[Measurement Conditions]':
                category = 1
            elif line == '[Results]':
                category = 2
            elif line == '[General Information]':
                category = 3
            elif line == 'Data':
                category = 4
            else:
                # try:
                if line.find('=') != -1:  # if there is '=' in a single line
                    strKey, strValue = line.split('=')
                    key = strKey.strip()
                    strValue = strValue.strip()
                    endidx = strKey.find('[')
                    if endidx != -1:
                        key = key[:endidx].strip()
                    try:  # trying to make value float
                        value = float(strValue)
                    except ValueError:  # if error, let it be string
                        value = strValue

                elif line.find('\t') != -1:  # if there is 'tab' in a single line
                    strKey, strValue = line.split('\t')
                    key = float(strKey.strip())
                    value = float(strValue.strip())
                else:    # if there is no '=' or 'tab'
                    line = file.readline()  # continue to read next
                    continue

                if category == 1:
                    self._measurement_conditions[key] = value

                elif category == 2:
                    self._results[key] = value

                elif category == 3:
                    self._general_information[key] = value

                elif category == 4:
                    self._sp_ird[float(key)] = value

                else:  # type == 0
                    pass

            line = file.readline()

        return True

    def _set_wl_ratio(self, alg='rect'):
        """
        파장비율 계산
        :param alg: 적분 알고리즘 선택, 'rect': 직사각형 공식, 'trapezoid': 사다리꼴 공식
        :return:
        """
        bird_vis = self.get_ird(380, 780, alg=alg)
        bird_sw = self.get_ird(380, 480, alg=alg)
        bird_mw = self.get_ird(480, 560, alg=alg)
        bird_lw = self.get_ird(560, 780, alg=alg)
        bird_narrow = self.get_ird(446, 477, alg=alg)

        if bird_vis == 0:
            self._results['swr'] = 0
            self._results['mwr'] = 0
            self._results['lwr'] = 0
            self._results['narr'] = 0
        else:
            self._results['swr'] = bird_sw / bird_vis
            self._results['mwr'] = bird_mw / bird_vis
            self._results['lwr'] = bird_lw / bird_vis
            self._results['narr'] = bird_narrow / bird_vis

    def _set_uv_ird(self, alg='rect'):
        """
        uv 계산
        :param alg: 적분 알고리즘 선택, 'rect': 직사각형 공식, 'trapezoid': 사다리꼴 공식
        :return:
        """
        self._uv['tuv'] = self.get_ird(280, 400, alg=alg)
        self._uv['uva'] = self.get_ird(315, 400, alg=alg)
        self._uv['uvb'] = self.get_ird(280, 315, alg=alg)
        self._uv['euv'] = self.get_ird(280, 400, weight_func='ery', alg=alg)
        self._uv['euva'] = self.get_ird(315, 400, weight_func='ery', alg=alg)
        self._uv['euvb'] = self.get_ird(280, 315, weight_func='ery', alg=alg)
        self._uv['uvi'] = self._uv['euv'] * 40
        self._uv['duv'] = self.get_ird(280, 400, weight_func='vitd', alg=alg)

        if self._uv['euv'] == 0:
            self._uv['euva_ratio'] = 0
            self._uv['euvb_ratio'] = 0
        else:
            self._uv['euva_ratio'] = self._uv['euva'] / self._uv['euv']
            self._uv['euvb_ratio'] = self._uv['euvb'] / self._uv['euv']

        self._uv['auv'] = self.get_ird(200, 400, weight_func='actinic_uv', alg=alg)

    def set_additional_data(self):
        self._general_information['file_abs_path'] = self.fname
        self._general_information['file_name'] = self.fname.split('\\')[1]

        self._measurement_conditions['CCDTemperature'] = float(self._measurement_conditions['CCDTemperature'].split()[0])
        self._measurement_conditions['DCCCDTemperature'] = float(self._measurement_conditions['DCCCDTemperature'].split()[0])

    def get_datetime(self, tostr=False):
        """
        측정시간 객체를 반환
        :param tostr: 문자열로 반환하려면 True
        :return: 측정시간 정보 :type: datetime or str
        """
        if tostr:
            if self.objDatetime:
                return self.objDatetime.strftime('%Y-%m-%d %H:%M:%S')
            else:
                return self._general_information['Date'] + ' ' + self._general_information['Time']
        else:
            if self.objDatetime:
                return self.objDatetime
            else:
                if self.debug:
                    Log.e(self.tag + '.get_datetime()')
                return None

    def get_category(self, category='all', str_key_type=False, to_json=False):
        """
        ISD 파일의 큰 범주에 해당하는 전체 데이터를 dictionary 형태로 반환
        :param category: 범주 이름
        :param str_key_type: True이면 key type을 문자열('str')로 변경, bson 호환성 위함
        :param to_json: json으로 반환
        :return: 범주 데이터 집합, :type: dictionary or json
        """

        # MongoDB의 기본 데이터형식인 bson은 key가 무조건 str이어야한다...
        # 그래서 str type key가 아닌 유일한 dict category인 spectral irradiance data dict에 대해
        # key type change code가 필요하다
        sp_ird = {}
        if str_key_type:
            keyset = self._sp_ird.keys()
            for key in keyset:
                sp_ird[str(key).replace('.', '_')] = self._sp_ird[key]

        d = {}
        if category == 'measurement_conditions':
            d = self._measurement_conditions
        elif category == 'results':
            d = self._results
        elif category == 'general_information':
            d = self._general_information
        elif category == 'sp_ird':
            d = sp_ird if str_key_type else self._sp_ird
        elif category == 'uv':
            d = self._uv

        elif category == 'all':
            d = {'datetime': self.get_datetime(True),
                 'data': {
                    'measurement_conditions': self._measurement_conditions,
                    'results': self._results,
                    'general_information': self._general_information,
                    'sp_ird': sp_ird if str_key_type else self._sp_ird,
                    'uv': self._uv
                    }
                 }

        elif category == 'except_sp_ird':
            d = {'datetime': self.get_datetime(True),
                 'data': {
                    'measurement_conditions': self._measurement_conditions,
                    'results': self._results,
                    'general_information': self._general_information,
                    'uv': self._uv
                    }
                 }
        elif category == 'simple':
            d = {'datetime': self.get_datetime(True)}

            for k in self._general_information.keys():
                try:
                    new_key = self.newkeymap[k]
                    d[new_key] = self._general_information[k]
                except KeyError:
                    continue

            for k in self._measurement_conditions.keys():
                try:
                    new_key = self.newkeymap[k]
                    d[new_key] = self._measurement_conditions[k]
                except KeyError:
                    continue

            for k in self._results.keys():
                try:
                    new_key = self.newkeymap[k]
                    d[new_key] = self._results[k]
                except KeyError:
                    continue

            for k in self._uv.keys():
                try:
                    new_key = self.newkeymap[k]
                    d[new_key] = self._uv[k]
                except KeyError:
                    continue

        if to_json:
            import json
            return json.dumps(d, indent=2)
        else:
            return d

    def get_attrib(self, item=None):
        """
        entity 하나에 대한 광특성 요소 추출
        :param item: 광특성 이름 (ISD 파일에 나와있는 이름, uv와 파장비율 등은 상기 코드에 정의된 이름으로 써야함)
        :return: 광특성 값, :type: str
        """
        keyset_mc = self._measurement_conditions.keys()
        keyset_re = self._results.keys()
        keyset_gi = self._general_information.keys()
        keyset_da = self._sp_ird.keys()
        keyset_uv = self._uv.keys()

        if item in keyset_mc:
            return self._measurement_conditions[item]
        elif item in keyset_re:
            return self._results[item]
        elif item in keyset_gi:
            return self._general_information[item]
        elif item in keyset_da:
            return self._sp_ird[item]
        elif item in keyset_uv:
            return self._uv[item]
        else:
            return None

    @staticmethod
    def search(dirname):
        """
        dirname 디렉토리 내의 모든 파일과 디렉토리 이름을 리스트로 반환함
        :param dirname: ISD 파일 들어있는 디렉토리 경로, :type: str
        :return: 모든 isd 파일의 절대경로, :type: list[str]
        """
        filelist = []
        filenames = os.listdir(dirname)
        for filename in filenames:
            full_filename = os.path.join(dirname, filename)
            filelist.append(full_filename)
        return filelist

    def get_ird(self, range_val_left, range_val_right, weight_func='none', alg='rect'):
        """
        분광 데이터 테이블로부터 특정 범위에 대한 광파장 복사량(broadband irradiance)을 float 단일값으로 반환 (광파장복사량 == 적산 값)
        :param range_val_left: 적분구간 시작 값
        :param range_val_right: 적분구간 끝 값
        :param weight_func: 가중함수 선택, 홍반가중함수('ery'), 비타민 d 가중함수('vitd'), 없음('none')
        :param alg: 적분 알고리즘 선택, 기본값('rect')은 직사각형 공식, 'trapezoid' 로 설정하면 사다리꼴 공식 적용
        :return: 파장 복사량(broadband irradiance),  :type: float
        """
        ird = 0
        if self._sp_ird:
            wls = list(self._sp_ird.keys())

            # for debug
            # print(wls)

            for i in range(len(wls) - 2):
                wll = float(wls[i])
                wlr = float(wls[i+1])
                irdl = self._sp_ird[wll]
                irdr = self._sp_ird[wlr]

                if irdl < 0 or irdr < 0:  # filter noise (negative value)
                    continue

                if weight_func == 'ery':
                    from entries.ref_func import erythemal_action_spectrum as eryf
                    weightl = eryf(wll)
                    weightr = eryf(wlr)
                elif weight_func == 'vitd':
                    from entries.ref_func import vitd_weight_func_interpolated as vitdf
                    weightl = vitdf(wll)
                    weightr = vitdf(wlr)
                elif weight_func == 'actinic_uv':
                    from entries.ref_func import actinic_uv_weight_func as actuvf
                    weightl = actuvf(wll)
                    weightr = actuvf(wlr)
                else:
                    weightl = 1
                    weightr = 1

                if range_val_left <= wll < range_val_right:
                    try:
                        # calculate weighted integration
                        if alg == 'trapezoid':
                            e = 0.5 * (wlr - wll) * (irdl * weightl + irdr * weightr)
                        else:  # alg == 'rect'
                            # print(str(wll) + '\t' + str(irdl*weightl))
                            e = (wlr - wll) * (irdl * weightl)
                    except TypeError:
                        print('get_ird(): spectral irradiance value exception!')
                        break

                    ird += e
                else:
                    pass

            return ird
        else:
            return


if __name__ == '__main__':
    import pprint
    rootdir = 'D:/test'
    flist = CasEntry.search(rootdir)

    for fname in flist:
        print('>>', fname)
        entity = CasEntry(fname)
        d = entity.get_category(category='simple')
        pprint.pprint(d)
        break


