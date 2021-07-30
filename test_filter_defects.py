

def _match_conditions(self, defect, conditions):
    if not conditions:
        return False

    for cond, val in conditions.items():
        if cond == 'locations':
            if defect['loc'] not in conditions['locations']:
                return False
        elif cond == 'subclass':
            if defect.get('subclass',None) is None:
                continue
            if defect.get('subclass', None) not in val:
                return False
        else:
            if not (val[0] <= defect[cond] < val[1]):
                return False

    return True


rules_by_class = {}


def is_component_ok(self, defects):
    '''判断组件是否ok'''
    # 如果没有缺陷，则为良品
    if not defects:
        return True

    # 返回是否为良品
    defect_cls = [x['class'] for x in defects]
    rule_cls = rules_by_class.keys()
    # 若存在缺陷没有定义捞回规则，这组件为不良品
    if set(defect_cls)-set(rule_cls):
        print('组件配方中若存在缺陷没有定义捞回规则, 判定组件为不良品, defect_cls:{}|rule_cls:{}'.format(defect_cls, rule_cls))
        return False

    # 至此，所有缺陷都存在相应捞回规则，如有任何捞回规则不满足，则为不良品，相反，
    # 若所有捞回规则都满足了，则为良品
    for cls, rules in rules_by_class.items():
        defect_cls = [x for x in defects if x['class'] == cls]
        if not defect_cls:
            continue
        for rule in rules:
            defect_per_cell = {}
            for defect in defect_cls:
                if _match_conditions(defect, rule['conditions']):
                    defect['rule_matched'] = True
                    loc = tuple(defect['loc'])
                    defect_per_cell.setdefault(loc, [0])[0] += 1
            bad_cells = 0
            for loc, num_l in defect_per_cell.items():
                if num_l[0] > rule['max_defects_per_cell']:
                    bad_cells += 1

            if bad_cells > rule['max_cells_per_compoment']:
                print('组件配方中{}中不满足{}规则, bad_cells:{}, 判定组件为不良品'.format(cls, rule, bad_cells))
                return False

    any_defect_not_covered = False  # 是否存在缺陷没有被任何规则覆盖
    for defect in defects:
        if 'rule_matched' not in defect:
            any_defect_not_covered = True
            print('组件配方中存在缺陷没有被任何规则覆盖，rule_matched not in {}, 判定组件为不良品。'.format(defect))
        else:
            del defect['rule_matched']
    if any_defect_not_covered:
        return False

    return True


defects = [{'grid_h': 581, 'grid_w': 316, 'grid_area': 183596, 'grid_diag': 661.3750826875776, 'grid_coord': (16, 11, 332, 592), 'defect_h': 45, 'h_ratio': 0.0774526678141136, 'defect_w': 56, 'w_ratio': 0.17721518987341772, 'defect_area': 2520, 'area_ratio': 0.01372578923288089, 'defect_diag': 71.84010022264724, 'diag_ratio': 0.10862232657861301, 'angle': 38.784364100297346, 'h_w_ratio': 0.8035714285714286, 'corner_dist_lt': 450.05444115129006, 'corner_dist_lb': 86.28441342444185, 'corner_dist_rt': 516.2450968290159, 'corner_dist_rb': 267.21714016881475, 'corner_dist_ratio_lt': 0.6804829104272261, 'corner_dist_ratio_lb': 0.13046214724905375, 'corner_dist_ratio_rt': 0.780563269379898, 'corner_dist_ratio_rb': 0.4040326694542915, 'corner_dist_ratio_min': 0.13046214724905375, 'edge_dist_top': 450, 'edge_dist_bottom': 86, 'edge_dist_left': 7, 'edge_dist_right': 253, 'edge_dist_ratio_top': 0.774526678141136, 'edge_dist_ratio_bottom': 0.14802065404475043, 'edge_dist_ratio_left': 0.022151898734177215, 'edge_dist_ratio_right': 0.8006329113924051, 'edge_dist_ratio_min_hor': 0.022151898734177215, 'edge_dist_ratio_min_ver': 0.14802065404475043, 'edge_dist_ratio_min': 0.022151898734177215, 'class': 'yinlie', 'prob': 0.9986535310745239, 'loc': [1, 1], 'coord': [23, 461, 79, 506]}, {'grid_h': 581, 'grid_w': 316, 'grid_area': 183596, 'grid_diag': 661.3750826875776, 'grid_coord': (645, 11, 961, 592), 'defect_h': 45, 'h_ratio': 0.0774526678141136, 'defect_w': 54, 'w_ratio': 0.17088607594936708, 'defect_area': 2430, 'area_ratio': 0.013235582474563716, 'defect_diag': 70.2922470831599, 'diag_ratio': 0.10628197058395193, 'angle': 39.80557109226519, 'h_w_ratio': 0.8333333333333334, 'corner_dist_lt': 429.16779935125606, 'corner_dist_lb': 107.67079455451233, 'corner_dist_rt': 496.5289518245638, 'corner_dist_rb': 271.93565415369864, 'corner_dist_ratio_lt': 0.6489022803932692, 'corner_dist_ratio_lb': 0.16279838381116363, 'corner_dist_ratio_rt': 0.7507524320493878, 'corner_dist_ratio_rb': 0.41116706884186693, 'corner_dist_ratio_min': 0.16279838381116363, 'edge_dist_top': 429, 'edge_dist_bottom': 107, 'edge_dist_left': 12, 'edge_dist_right': 250, 'edge_dist_ratio_top': 0.7383820998278829, 'edge_dist_ratio_bottom': 0.18416523235800344, 'edge_dist_ratio_left': 0.0379746835443038, 'edge_dist_ratio_right': 0.7911392405063291, 'edge_dist_ratio_min_hor': 0.0379746835443038, 'edge_dist_ratio_min_ver': 0.18416523235800344, 'edge_dist_ratio_min': 0.0379746835443038, 'class': 'yinlie', 'prob': 0.9982806444168091, 'loc': [1, 3], 'coord': [657, 440, 711, 485]}, {'grid_h': 581, 'grid_w': 319, 'grid_area': 185339, 'grid_diag': 662.8136993152751, 'grid_coord': (1276, 11, 1595, 592), 'defect_h': 215, 'h_ratio': 0.37005163511187605, 'defect_w': 310, 'w_ratio': 0.9717868338557993, 'defect_area': 66650, 'area_ratio': 0.3596113068485316, 'defect_diag': 377.25985739275256, 'diag_ratio': 0.5691793301533806, 'angle': 34.74318015830361, 'h_w_ratio': 0.6935483870967742, 'corner_dist_lt': 248.47132631352054, 'corner_dist_lb': 122.0245876862528, 'corner_dist_rt': 247.65500196846418, 'corner_dist_rb': 120.3536455617361, 'corner_dist_ratio_lt': 0.374873552810097, 'corner_dist_ratio_lb': 0.1841008835700156, 'corner_dist_ratio_rt': 0.37364194829453, 'corner_dist_ratio_rb': 0.18157990048496037, 'corner_dist_ratio_min': 0.18157990048496037, 'edge_dist_top': 247, 'edge_dist_bottom': 119, 'edge_dist_left': 27, 'edge_dist_right': 18, 'edge_dist_ratio_top': 0.42512908777969016, 'edge_dist_ratio_bottom': 0.20481927710843373, 'edge_dist_ratio_left': 0.08463949843260188, 'edge_dist_ratio_right': 0.05642633228840126, 'edge_dist_ratio_min_hor': 0.05642633228840126, 'edge_dist_ratio_min_ver': 0.20481927710843373, 'edge_dist_ratio_min': 0.05642633228840126, 'class': 'yinlie', 'prob': 0.9987609386444092, 'loc': [1, 5], 'coord': [1303, 258, 1613, 473]}]

is_ng = not is_component_ok(defects)
print(is_ng)
