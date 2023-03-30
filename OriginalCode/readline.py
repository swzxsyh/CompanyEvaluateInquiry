# 测试，读取json文件
import json
from OriginalCode.Company import Company

# 读取文件
def read_companys_json():
    file = open("../Companys.json")
    lines = file.read()
    file.close()
    return lines


# 过滤 _comment 字段
def ignore_comment_pairs(pairs):
    return [(k, v) for k, v in pairs if k != '_comment']


# 序列化JSON
def parse_jsonStr_to_json(json_str):
    data = json.loads(json_str, object_pairs_hook=ignore_comment_pairs)
    return data


# 将JSON对象转换为Company对象
def from_json(json_obj):
    company_data = json_obj[1]
    return Company(company_data["company_name"], company_data["api_url"], company_data["token"], company_data["mapping"], company_data["type"])


# 公司列表赋值
def initial_company_array(json_str):
    companies = []  # 创建空的公司列表
    json_obj = json.loads(json_str)
    for key, value in json_obj.items():  # 遍历json_obj中的键和值对
        if key != "_comment":
            company = from_json((key, value))  # 将值对传递给from_json函数以创建公司对象
            companies.append(company)  # 将公司对象添加到列表中
    return companies


if __name__ == '__main__':
    json_str = read_companys_json()

    company_array = initial_company_array(json_str)
    print("array: ", company_array[0].company_name)