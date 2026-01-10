import { app } from "/scripts/app.js";
import { ComfyWidgets } from "/scripts/widgets.js";


function NCEUtilsShowTextNodeCreated(nodeType, nodeData) {
	const onnNodeCreated = nodeType.prototype.onNodeCreated;

	// 定义 populate 函数（在外层，避免重复创建）
	function populate(text, source) {
		console.log(`NCEUtilsShowText - populate called from: ${source}`);
		console.log("NCEUtilsShowText - text:", text);
		console.log("NCEUtilsShowText - current widgets count:", this.widgets?.length || 0);

		// 防止重复调用：如果已经在处理中，跳过
		if (this._isPopulating) {
			console.log("NCEUtilsShowText - SKIPPED: already populating");
			return;
		}
		this._isPopulating = true;

		// 清除所有旧的 widgets（包括第一个）
		if (this.widgets) {
			for (let i = 0; i < this.widgets.length; i++) {
				this.widgets[i].onRemove?.();
			}
			this.widgets.length = 0;
		}

		// 处理 text 数据
		let v = [];
		if (Array.isArray(text)) {
			v = [...text];
		} else {
			v = [text];
		}

		// 移除空元素
		if (!v[0]) {
			v.shift();
		}

		console.log("NCEUtilsShowText - will create", v.length, "widgets");

		for (const list of v) {
			const w = ComfyWidgets["STRING"](this, "text", ["STRING", { multiline: true }], app).widget;
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

			// 重置标志
			this._isPopulating = false;
		});
	}

	nodeType.prototype.onNodeCreated = function () {
		onnNodeCreated?.apply(this, arguments);
	}

	// 将事件处理器定义在外层，避免重复绑定
	const onExecuted = nodeType.prototype.onExecuted;
	nodeType.prototype.onExecuted = function (message) {
		console.log("NCEUtilsShowText - onExecuted called");
		onExecuted?.apply(this, arguments);
		populate.call(this, message.text, "onExecuted");
	};

	const onConfigure = nodeType.prototype.onConfigure;
	nodeType.prototype.onConfigure = function () {
		console.log("NCEUtilsShowText - onConfigure called, widgets_values:", this.widgets_values);
		onConfigure?.apply(this, arguments);
		if (this.widgets_values?.length) {
			populate.call(this, this.widgets_values.slice(+this.widgets_values.length > 1), "onConfigure");
		}
	};
}

function NCEMergeTextsNodeCreated(nodeType, nodeData, app) {
	const onnNodeCreated = nodeType.prototype.onNodeCreated
	nodeType.prototype.onNodeCreated = function () {
		onnNodeCreated?.apply(this, arguments);

		const input_name = getInputName(nodeData.name);

		// 初始化 origin_type 属性
		if (!this.origin_type) {
			this.origin_type = "STRING";
		}

		// 确保节点创建时有 input_1
		const hasInputs = this.inputs && this.inputs.some(input => input.name.includes(input_name));
		if (!hasInputs) {
			this.addInput(`${input_name}1`, this.origin_type);
		}
	}

	// 将 onConnectionsChange 定义在外层，而不是嵌套在 onNodeCreated 内部
	const onConnectionsChange = nodeType.prototype.onConnectionsChange;
	nodeType.prototype.onConnectionsChange = function (
		type,
		index,
		connected,
		link_info
	) {
		if (!link_info) return;
		if (type == 1) {
			const input_name = getInputName(nodeData.name);
			handleInputConnection(this, link_info, app, input_name);
			const specialInputCount = countSpecialInputs(this);
			const select_slot = this.inputs.find((x) => x.name == "select");

			handleInputRemoval(this, index, connected, specialInputCount);
			renameInputs(this, input_name);
			updateWidgets(this, input_name, select_slot);
		}

		// 调用原始的 onConnectionsChange
		onConnectionsChange?.apply(this, arguments);
	};
}

function getInputName(nodeName) {
	return "input_";
}

function countSpecialInputs(node) {
	const specialInputs = ["select", "sel_mode", "merge_string"];
	return node.inputs.filter((input) => specialInputs.includes(input.name))
		.length;
}

function handleInputConnection(node, link_info, app, input_name) {
	const origin_node = app.graph.getNodeById(link_info.origin_id);
	let origin_type = origin_node.outputs[link_info.origin_slot].type;

	if (origin_type == "*") {
		node.disconnectInput(link_info.target_slot);
		return;
	}

	// 保存 origin_type 到节点属性
	node.origin_type = origin_type;

	// 更新所有动态输入的类型（排除特殊输入）
	for (let i in node.inputs) {
		let input_i = node.inputs[i];
		if (input_i.name != "select" && input_i.name != "sel_mode" && input_i.name != "merge_string") {
			input_i.type = origin_type;
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

		// 只移除动态输入，不移除特殊输入
		if (isValidRemovalContext(stackTrace) &&
			inputToRemove.name !== "select" &&
			inputToRemove.name !== "sel_mode" &&
			inputToRemove.name !== "merge_string") {
			node.removeInput(index);
		}
	}
}

function renameInputs(node, input_name) {
	let slot_i = 1;
	// 只重命名动态输入（input_1, input_2, ...），不重命名特殊输入
	for (let i = 0; i < node.inputs.length; i++) {
		let input_i = node.inputs[i];
		if (input_i.name != "select" && input_i.name != "sel_mode" && input_i.name != "merge_string") {
			input_i.name = `${input_name}${slot_i}`;
			slot_i++;
		}
	}

	// 获取最后一个动态输入（排除所有特殊输入）
	let last_dynamic_input = null;
	for (let i = node.inputs.length - 1; i >= 0; i--) {
		let input = node.inputs[i];
		if (input.name != "select" && input.name != "sel_mode" && input.name != "merge_string") {
			last_dynamic_input = input;
			break;
		}
	}

	// 如果最后一个动态输入有连接，则添加新的输入槽位
	if (last_dynamic_input && last_dynamic_input.link != undefined) {
		node.addInput(`${input_name}${slot_i}`, node.origin_type || "STRING");
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
		if (!nodeData?.category?.startsWith("🐍 NCE")) return;
		console.log(nodeData.name)
		switch (nodeData?.name) {
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
