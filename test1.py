[
    {
        "label": "YGFC-03B",
        "children": [
            {
                "label": "YGFC-03B-VC3+1R",
                "children": [
                    {
                        "label": "YGFC-03B-VC 3+1R STD 亲水铝箔 COIL组件左",
                    }
                ],
            }
        ],
    }
]

test_data = [
    {"key": "YGFC-03B-VC 3+1R STD 亲水铝箔 COIL组件左"},
    {"key": "YGFC02-H 2R STD 亲水铝箔 COIL组件右"},
    {"key": "YGFC02-H 2R STD 亲水铝箔 COIL组件左"},
    {"key": "YGFC-03B-VC 3+1R STD 亲水铝箔 COIL组件右"},
]


def main():
    return_data = []
    parent = set()
    children = set()
    grandson = set()

    for materiel in test_data:
        materiel_name = materiel.get("key")  # YGFC02-H 2R 亲水铝箔COIL组件左
        materiel_split_name = materiel_name.split(
            " ", 2
        )  # ['YGFC02-H', '2R', '亲水铝箔COIL组件左']

        if len(materiel_split_name) == 3:
            for name in materiel_split_name:
                if "YGFC" in name:
                    v1 = name.rsplit("-", 1)
                    parent.add(v1[0])

        children.add(materiel_split_name[0] + " " + materiel_split_name[1])
        grandson.add(materiel_name)

    for i in parent:
        parent_dict = {"label": i, "children": []}

        for j in children:
            children_dict = {"label": j, "children": []}

            if i in j:
                # j 是 i 的子分类，把j 加到父类的children中
                parent_dict["children"].append(children_dict)

            for k in grandson:
                if j in k:
                    # 同理 k是j的子分类，把k加大j的children中
                    # k = k.split("#")[1]
                    grandson_dict = {"label": k}
                    children_dict["children"].append(grandson_dict)

        return_data.append(parent_dict)
    print(return_data)


if __name__ == "__main__":
    main()
    pass
