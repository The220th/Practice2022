# -*- coding: utf-8 -*-

from dash import html, Dash
import dash_cytoscape as cyto
from dash.dependencies import Input, Output

import json
import os
import sys

class Global():
    folderpath = None

# http://127.0.0.1:8050/
app = Dash(__name__)

def getOutStyle() -> dict:
    return {
    'pre': {
        'border': 'thin lightgrey solid',
        #'overflowX': 'scroll',
        #'overflowX': 'visible',
        'overflowX': 'hidden',
        "white-space": "pre-wrap",
        "font-size": "20px",
        'position': 'absolute',
        'background-color':'white',
        'max-height':'20%',
        'width': 'calc(100vw - 38px)',
        'padding': '10px',
        'margin': '0'
    }
}

def getStylesheet() -> list:
    # https://dash.plotly.com/cytoscape/styling
    style = [
            {
                'selector': 'node',
                'style': {
                    'background-color': '#BFD7B5',
                    'content': 'data(label)'
                }
            },
            {
                'selector': '.before',
                'style': {
                    'background-color': 'blue',
                    'line-color': 'blue',
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                }
            },
            {
                'selector': '.after',
                'style': {
                    'background-color': 'red',
                    'line-color': 'red',
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                }
            },
            {
                'selector': '.triangle',
                'style': {
                    'shape': 'triangle',
                    'background-color': 'red'
                }
            }
    ]
    return style

def normalize_text(s : str, where_wrap: int) -> str:
    res = ""
    N = len(s)
    i = where_wrap
    i_prev = 0
    while(i < N+where_wrap):
        res += s[i_prev:i] + "\n\n"
        i_prev = i
        i+=where_wrap
    return res[:-1]

def getElements() -> list:
    SYMBOLS_NUM = 12 # Количество отображаемых символов перед переносом

    folderpath = Global.folderpath 
    files_buff = [os.path.join(path, name) for path, subdirs, files in os.walk(folderpath) for name in files]
    all_sub = {}
    all_edges = []
    edge_id = 0
    for filepath in files_buff:
        d = json.load(open(filepath, "r", encoding="utf-8"))
        cur_id = d["title"]["planNameSubjects"]["id"]
        cur_sub_name = d["title"]["planNameSubjects"]["subject"]
        before = d["generalProv"]["nameBeforeSubjectRows"]
        after = d["generalProv"]["nameAfterSubjectRows"]
        if(cur_id in all_sub and cur_sub_name != all_sub[cur_id]):
            print(f"WARNING: ID ({cur_id}) is the same, but name is defferent: {cur_sub_name} and {all_sub[cur_id]}. Check file {filepath}. ")
        all_sub[cur_id] = cur_sub_name
        for before_i in before:
            if(before_i["id"] in all_sub and before_i["nameSubject"] != all_sub[before_i["id"]]):
                print(f"WARNING: ID ({before_i['id']}) is the same, but name is defferent: {before_i['nameSubject']} and {all_sub[before_i['id']]}. Check file {filepath}. ")
            all_sub[before_i["id"]] = before_i["nameSubject"]
            all_edges.append({"data" : {"id" : f"eb{edge_id}", "source" : f"{before_i['id']}", "target" : f"{cur_id}"},  "classes" : "before"})
            edge_id+=1
        for after_i in after:
            if(after_i["id"] in all_sub and after_i["nameSubject"] != all_sub[after_i["id"]]):
                print(f"WARNING: ID ({after_i['id']}) is the same, but name is defferent: {after_i['nameSubject']} and {all_sub[after_i['id']]}. Check file {filepath}. ")
            all_sub[after_i["id"]] = after_i["nameSubject"]
            all_edges.append({"data" : {"id" : f"ea{edge_id}", "source" : f"{cur_id}", "target" : f"{after_i['id']}"}, "classes" : "after"})
            edge_id+=1
    all_k = all_sub.keys()
    all_vertex = []
    for k in all_k:
        #all_vertex.append({"data" : {"id" : f"{k}", "label" : f"{normalize_text(all_sub[k], SYMBOLS_NUM)}", "sub_name" : f"{all_sub[k]}"}})
        all_vertex.append({"data" : {"id" : f"{k}", "label" : f"{all_sub[k][:SYMBOLS_NUM]}", "sub_name" : f"{all_sub[k]}"}})

    # Отобразить ошибки
    # Если предмет a говорит, что дальше можно обучаться предмету b (classes == after and target == b), 
    # а предмет b готорит, что ему не нужен предмет a (classes == before and not (source == a and target == b))
    for k_int in all_k:
        k = f"{k_int}"
        for e_i in all_edges:
            if(e_i["classes"] == "after" and e_i["data"]["target"] == k):
                error_flag = True
                k_source = e_i["data"]["source"]
                for v_i in all_vertex:
                    if(v_i["data"]["id"] == k_source):
                        name_source = v_i["data"]["sub_name"]
                        break

                # Найти в before, что target == k, тогда ошибки нет
                for e2_i in all_edges:
                    if(e2_i["classes"] == "before" and e2_i["data"]["source"] == k_source and e2_i["data"]["target"] == k):
                        error_flag = False
                        break
                
                if(error_flag == True):
                    #print(e_i)
                    for v_i in all_vertex:
                        if(v_i["data"]["id"] == k):
                            subID = v_i["data"]["id"]
                            subNAME = v_i["data"]["sub_name"]
                            sub1 = f"\"{name_source}\" (id={k_source})"
                            sub2 = f"\"{subNAME}\" (id={subID})"
                            erMsg = f"⚠️ Предмет {sub1} говорит, что дальше нужно изучать {sub2}, но {sub2} не требует изучение {sub1}. \n\n"
                            if "error_msg" not in v_i["data"]:
                                v_i["data"]["error_msg"] = erMsg
                                v_i["classes"] = "triangle"
                            else:
                                v_i["data"]["error_msg"] += erMsg
    
    # Ищем одиннаковые названия
    if(True):
        for i in range(len(all_vertex)):
            v_name = all_vertex[i]["data"]["sub_name"]
            err_text = "⛔ Такие же имена имеют id: "
            if_err_text = False
            for j in range(len(all_vertex)):
                if(j == i):
                    continue
                if(all_vertex[j]["data"]["sub_name"] == v_name):
                    err_text += f"{all_vertex[j]['data']['id']} "
                    if_err_text = True
            err_text += "\n\n"
            if(if_err_text):
                if "error_msg" not in all_vertex[i]["data"]:
                    all_vertex[i]["data"]["error_msg"] = err_text
                    all_vertex[i]["classes"] = "triangle"
                else:
                    all_vertex[i]["data"]["error_msg"] += err_text
    
    d_max_root = {}
    for e_i in all_edges:
        sID = e_i["data"]["source"]
        if(sID not in d_max_root):
            d_max_root[sID] = 1
        else:
            d_max_root[sID]-=-1
    kk = d_max_root.keys()
    # kk_max = 0
    # kk_nmax = None
    # for kk_i in kk:
    #     if(d_max_root[kk_i] > kk_max):
    #         kk_max = d_max_root[kk_i]
    #         kk_nmax = kk_i
    # Global.rootIDs = kk_nmax

    a_roots = []
    for kk_i in kk:
       a_roots.append([kk_i, d_max_root[kk_i]])
    ROOTS_NUM = int(len(a_roots)*0.1)
    buff = sorted(a_roots, key=lambda x : x[1], reverse=True)[:ROOTS_NUM]
    Global.rootIDs = []
    for item in buff:
        Global.rootIDs.append(item[0])

                

    
    return all_vertex + all_edges

@app.callback(Output('cytoscape-tapNodeData-json', 'children'),
              Input('practice_part2', 'tapNodeData'))
def displayTapNodeData(data):
    #return json.dumps(data)
    if(data == None or data["sub_name"] == None):
        return "None"
    res = f"{data['sub_name']} (id={data['id']})\n"
    if("error_msg" in data):
        res += f"\n{data['error_msg']}"
    return res

if __name__ == '__main__':
    buffPath = sys.argv[1]
    buffPath = os.path.abspath(buffPath)
    if(os.path.isdir(buffPath) == False):
        print("Folder does not exist. ")
        exit()
    Global.folderpath = buffPath

    l_elements = getElements()
    l_stylesheet = getStylesheet()
    app.layout = html.Div([
        cyto.Cytoscape(
                id = "practice_part2",
                #layout = {"name" : "random"},
                #layout = {"name" : "circle"},
                #layout = {"name" : "breadthfirst"},
                layout = {"name" : "breadthfirst", "roots" : Global.rootIDs},
                #style = {"width" : "100%", "height" : "720px"},
                #style = {"width" : "calc(100vw)", "height" : "calc(100vh)"},
                style = {"width" : "calc(100vw - 10px)", "height" : "calc(100vh - 10px)", "position":"absolute"},
                elements = l_elements,
                stylesheet = l_stylesheet
            ),
        html.Pre(id='cytoscape-tapNodeData-json', style = getOutStyle()['pre'])
        ])
    app.run_server(debug=True)