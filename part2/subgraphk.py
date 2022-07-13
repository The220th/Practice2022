# -*- coding: utf-8 -*-

from dash import html, Dash
import dash_cytoscape as cyto
import json
import os
import sys

class Global():
    folderpath = None

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
                    'line-color': 'blue'
                }
            },
            {
                'selector': '.after',
                'style': {
                    'background-color': 'red',
                    'line-color': 'red'
                }
            }
    ]
    return style

def getElements() -> list:
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
        all_vertex.append({"data" : {"id" : f"{k}", "label" : f"{k}"}})
    return all_vertex + all_edges

if __name__ == '__main__':
    buffPath = sys.argv[1]
    buffPath = os.path.abspath(buffPath)
    if(os.path.isdir(buffPath) == False):
        print("Folder does not exist. ")
        exit()
    Global.folderpath = buffPath

    # http://127.0.0.1:8050/
    app = Dash(__name__)
    app.layout = html.Div([
        cyto.Cytoscape(
                id = "test",
                layout = {"name" : "random"},
                style = {"width" : "100%", "height" : "1080px"},
                elements = getElements(),
                stylesheet = getStylesheet()
            )
        ])
    app.run_server(debug=True)