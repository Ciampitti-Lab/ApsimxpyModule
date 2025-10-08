from anytree import Node, RenderTree
import json
##################################################
# # Object: Object to inspect the model          #
##################################################
class HelpTree:
    def __init__(self, init_obj=None):
        self.apsim_file_input=init_obj.apsim_file_input
        apsim_file=open(f"/workspace/{self.apsim_file_input}.apsimx","r")
        apsim_json = apsim_file.read()
        self.simulations=json.loads(apsim_json)
    
    def main(self):
        root = Node("Simulations")
        for i,j in enumerate(self.simulations['Children']):
            child = Node(self.simulations['Children'][i]['Name'], parent=root)
            for k,m in enumerate(self.simulations['Children'][i]['Children']):
                grandchild = Node(self.simulations['Children'][i]['Children'][k]['Name'], parent=child)

        for pre, fill, node in RenderTree(root):
            print(f"{pre}{node.name}")
    
    def main_clock(self):
        models = self.simulations["Children"][0]["Children"]
        zones = next(child for child in models if child["$type"] == "Models.Clock, Models")
        root = Node("Clock")
        child = Node('Start Date: ' + zones['Start'], parent=root)
        child2 = Node('End Date: ' + zones['End'], parent=root)

        for pre, fill, node in RenderTree(root):
            print(f"{pre}{node.name}")
                