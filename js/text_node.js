import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";

function NCEUtilsShowTextNodeCreated(nodeType, nodeData){
	const onnNodeCreated = nodeType.prototype.onNodeCreated
	nodeType.prototype.onNodeCreated = function () {
		onnNodeCreated.apply(this, arguments);
		function populate(text) {
			if (this.widgets) {
				for (let i = 1; i < this.widgets.length; i++) {
					this.widgets[i].onRemove?.();
				}
				this.widgets.length = 1;
			}			
			const v = [...text];
			if (!v[0]) {
				v.shift();
			}
			for (const list of v) {
				const w = ComfyWidgets["STRING"](this, "text2", ["STRING", { multiline: true }], app).widget;
				w.inputEl.readOnly = true;
				w.inputEl.style.opacity = 0.6;
				w.value = list;
			}

			requestAnimationFrame(() => {
				const sz = this.computeSize();
				if (sz[0] < this.size[0]) {
					sz[0] = this.size[0];
				}
				if (sz[1] < this.size[1]) {
					sz[1] = this.size[1];
				}
				this.onResize?.(sz);
				app.graph.setDirtyCanvas(true, false);
			});
		}

		const onExecuted = nodeType.prototype.onExecuted;
		nodeType.prototype.onExecuted = function (message) {
			onExecuted?.apply(this, arguments);
			populate.call(this, message.text);
		};

		const onConfigure = nodeType.prototype.onConfigure;
		nodeType.prototype.onConfigure = function () {
			onConfigure?.apply(this, arguments);
			if (this.widgets_values?.length) {
				populate.call(this, this.widgets_values.slice(+this.widgets_values.length > 1));
			}
		};
	}
}

function NCEMergeTextsNodeCreated(nodeType, nodeData, app){
	const onnNodeCreated = nodeType.prototype.onNodeCreated
	nodeType.prototype.onNodeCreated = function () {
		onnNodeCreated.apply(this, arguments);

		const input_name = getInputName(nodeData.name)
		const onConnectionsChange = nodeType.prototype.onConnectionsChange;
		nodeType.prototype.onConnectionsChange = function (
		  type,
		  index,
		  connected,
		  link_info
		) {
		  if (!link_info) return;
		  if (type == 1) {
			handleInputConnection(this, link_info, app, input_name);
			const specialInputCount = countSpecialInputs(this);
			const select_slot = this.inputs.find((x) => x.name == "select");
	  
			handleInputRemoval(this, index, connected, specialInputCount);
			renameInputs(this, input_name);
			updateWidgets(this, input_name, select_slot);
		  }
		};
	}
}

function getInputName(nodeName) {
	return "input_";
}

function countSpecialInputs(node) {
	const specialInputs = ["select", "sel_mode"];
	return node.inputs.filter((input) => specialInputs.includes(input.name))
	  .length;
}

  function handleInputConnection(node, link_info, app, input_name) {
	const origin_node = app.graph.getNodeById(link_info.origin_id);
	let origin_type = origin_node.outputs[link_info.origin_slot].type;
  
	if (origin_type == "*") {
	  node.disconnectInput(link_info.target_slot);
	}
  
	for (let i in node.inputs) {
	  if (node.inputs[i].name.includes(input_name)) {
		let input_i = node.inputs[i];
		for (let i in node.inputs) {
		  let input_i = node.inputs[i];
		  if (input_i.name != "select" && input_i.name != "sel_mode")
			input_i.type = origin_type;
		}
	  }
	}
}
  
  function handleInputRemoval(node, index, connected, converted_count) {
	const CONNECT_TOUCH = "LGraphNode.prototype.connect";
	const CONNECT_MOUSE = "LGraphNode.connect";
	const LOAD_GRAPH = "loadGraphData";
  
	function isValidRemovalContext(stackTrace) {
	  return (
		!stackTrace.includes(CONNECT_TOUCH) &&
		!stackTrace.includes(CONNECT_MOUSE) &&
		!stackTrace.includes(LOAD_GRAPH)
	  );
	}
  
	if (!connected && node.inputs.length > 1 + converted_count) {
	  const stackTrace = new Error().stack;
	  const inputToRemove = node.inputs[index];
  
	  if (isValidRemovalContext(stackTrace) && inputToRemove.name !== "select") {
		node.removeInput(index);
	  }
	}
  }
  
  function renameInputs(node, input_name) {
	let slot_i = 1;
	for (let i = 0; i < node.inputs.length; i++) {
	  let input_i = node.inputs[i];
	  if (input_i.name != "select" && input_i.name != "sel_mode") {
		input_i.name = `${input_name}${slot_i}`;
		slot_i++;
	  }
	}
  
	let last_slot = node.inputs[node.inputs.length - 1];
	if (
	  (last_slot.name == "select" &&
		last_slot.name != "sel_mode" &&
		node.inputs[node.inputs.length - 2].link != undefined) ||
	  (last_slot.name != "select" &&
		last_slot.name != "sel_mode" &&
		last_slot.link != undefined)
	) {
	  node.addInput(`${input_name}${slot_i}`, node.origin_type);
	}
  }
  
  function updateWidgets(node, input_name, select_slot) {
	if (!node.widgets) return;
  
	const inputWidget = node.widgets.find((w) => w.name.includes(input_name));
	if (inputWidget) {
	  inputWidget.options.max = select_slot
		? node.inputs.length - 1
		: node.inputs.length;
	  inputWidget.value = Math.min(
		Math.max(1, inputWidget.value),
		inputWidget.options.max
	  );
	}
  }
  
app.registerExtension({
    name: "nce.utils.text",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if(!nodeData?.category?.startsWith("🐍 NCE")) return;
		console.log(nodeData.name)
		switch(nodeData?.name){
			case "NCEUtilsShowText":
				NCEUtilsShowTextNodeCreated(nodeType, nodeData)
				break
			case "NCEMergeTexts":
				console.log('NCEMergeTexts')
				NCEMergeTextsNodeCreated(nodeType, nodeData, app)
				break
		}
	},
});
