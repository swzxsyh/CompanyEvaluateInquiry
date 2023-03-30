# 定义自定义对象
class Company:
    def __init__(self, company_name, api_url, token, mapping, type):
        self.company_name = company_name
        self.api_url = api_url
        self.token = token
        self.mapping = mapping
        self.type = type
