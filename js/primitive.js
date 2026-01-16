import { app } from "/scripts/app.js";

app.registerExtension({
    name: "nce.utils.primitive",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (!nodeData?.category?.startsWith("🐍 NCE")) return;

        switch (nodeData?.name) {
            case "NCEIntConstant":
                // 整数常量节点外观
                const onNodeCreatedInt = nodeType.prototype.onNodeCreated;
                nodeType.prototype.onNodeCreated = function () {
                    onNodeCreatedInt?.apply(this, arguments);
                    this.setSize([200, 58]);
                    this.color = "#1b4669";
                    this.bgcolor = "#29699c";
                };
                break;

            case "NCEFloatConstant":
                // 浮点数常量节点外观
                const onNodeCreatedFloat = nodeType.prototype.onNodeCreated;
                nodeType.prototype.onNodeCreated = function () {
                    onNodeCreatedFloat?.apply(this, arguments);
                    this.setSize([200, 58]);
                    this.color = "#2a363b";
                    this.bgcolor = "#3f5159";

                    // 设置 widget 的精度显示
                    if (this.widgets) {
                        for (let widget of this.widgets) {
                            if (widget.type === "number" && widget.name === "value") {
                                // 设置显示精度为2位小数
                                widget.options = widget.options || {};
                                widget.options.precision = 2;
                            }
                        }
                    }
                };
                break;
        }
    },
});
