import { app } from "/scripts/app.js";

app.registerExtension({
    name: "nce.utils.image_info",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (!nodeData?.category?.startsWith("🐍 NCE")) return;

        if (nodeData?.name === "NCEGetImageSize") {
            // 连接输入时设置初始标签
            const onConnectInput = nodeType.prototype.onConnectInput;
            nodeType.prototype.onConnectInput = function (targetSlot, type, output, originNode, originSlot) {
                const v = onConnectInput ? onConnectInput.apply(this, arguments) : undefined;
                this.outputs[1]["label"] = "width";
                this.outputs[2]["label"] = "height";
                this.outputs[3]["label"] = "count";
                return v;
            };

            // 执行后更新标签显示实际值
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function (message) {
                const r = onExecuted ? onExecuted.apply(this, arguments) : undefined;

                if (message["text"]) {
                    let values = message["text"].toString().split('x').map(Number);
                    // 格式: count x width x height
                    this.outputs[1]["label"] = values[1] + " width";
                    this.outputs[2]["label"] = values[2] + " height";
                    this.outputs[3]["label"] = values[0] + " count";
                }

                return r;
            };
        }
    },
});
