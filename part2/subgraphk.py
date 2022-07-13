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
        'overflowX': 'scroll'
        #'overflowX': 'visible'
    }
}

def getStylesheet() -> list:
    # https://dash.plotly.com/cytoscape/styling
    style = [
            {
                'selector': 'node',
                'style': {
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

def getElements() -> list:
    SYMBOLS_NUM = 10 # Количество отображаемых символов

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
                            erMsg = f"* Предмет {sub1} говорит, что дальше нужно изучать {sub2}, но {sub2} не требует изучение {sub1}\n\n"
                            if "error_msg" not in v_i["data"]:
                                v_i["data"]["error_msg"] = erMsg
                                v_i["classes"] = "triangle"
                            else:
                                v_i["data"]["error_msg"] += erMsg
                

    
    return all_vertex + all_edges

@app.callback(Output('cytoscape-tapNodeData-json', 'children'),
              Input('practice_part2', 'tapNodeData'))
def displayTapNodeData(data):
    #return json.dumps(data)
    if(data == None or data["sub_name"] == None):
        return "None"
    res = f"{data['sub_name']} (if={data['id']})\n"
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

    app.layout = html.Div([
        cyto.Cytoscape(
                id = "practice_part2",
                #layout = {"name" : "random"},
                #layout = {"name" : "circle"},
                layout = {"name" : "breadthfirst"},
                #layout = {"name" : "breadthfirst", "roots" : [2026890]},
                style = {"width" : "100%", "height" : "720px"},
                elements = getElements(),
                stylesheet = getStylesheet()
            ),
        html.Pre(id='cytoscape-tapNodeData-json', style = getOutStyle()['pre'])
        ])
    app.run_server(debug=True)