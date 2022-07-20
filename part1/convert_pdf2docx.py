# -*- coding: utf-8 -*-

import requests as req

if __name__ == '__main__':
    pubKey = "project_public_kokokokekeke"
    pubKeyArg={"public_key":pubKey}
    r = req.post(f"https://api.ilovepdf.com/v1/auth", json=pubKeyArg)
    token = r.json()["token"]
    #ilovepdf dont have api for pdf_to_word: https://www.ilovepdf.com/ru/pdf_to_word
    #                                        https://developer.ilovepdf.com/docs/api-reference