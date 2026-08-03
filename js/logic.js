import { app } from "/scripts/app.js";
import { ComfyWidgets } from "/scripts/widgets.js";

function NCEShowAnythingNodeCreated(nodeType, nodeData) {
    const onNodeCreated = nodeType.prototype.onNodeCreated;

    // 定义 populate 函数
    function populate(text, source) {
        console.log(`NCEShowAnything - populate called from: ${source}`);
        console.log("NCEShowAnything - text:", text);

        // 防止重复调用
        if (this._isPopulating) {
            console.log("NCEShowAnything - SKIPPED: already populating");
            return;
        }
        this._isPopulating = true;

        // 清除所有旧的 widgets
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

        // 移除开头的空项
        if (v.length > 0 && !v[0] && v[0] !== 0) {
            v.shift();
        }

        for (let list of v) {
            if (!Array.isArray(list)) list = [list];
            for (const l of list) {
                const valStr = typeof l === "object" ? JSON.stringify(l, null, 2) : String(l ?? "");
                const w = ComfyWidgets["STRING"](this, "text_" + (this.widgets?.length || 0), ["STRING", { multiline: true }], app).widget;
                if (w && w.inputEl) {
                    w.inputEl.readOnly = true;
                    w.inputEl.style.opacity = "0.85";
                    w.inputEl.style.overflowY = "auto";
                    w.inputEl.style.overflowX = "auto";
                    w.inputEl.style.boxSizing = "border-box";
                }
                w.value = valStr;
            }
        }

        requestAnimationFrame(() => {
            const sz = this.computeSize();
            // 限制节点自动扩充的最大高度，长文本通过 textarea 内部滚动条(overflowY: auto)滚动查看
            if (sz[1] > 350) {
                sz[1] = 350;
            }
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
        onNodeCreated?.apply(this, arguments);
    };

    // 事件处理器
    const onExecuted = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function (message) {
        console.log("NCEShowAnything - onExecuted called");
        onExecuted?.apply(this, arguments);
        populate.call(this, message.text, "onExecuted");
    };

    const VALUES = Symbol();
    const configure = nodeType.prototype.configure;
    nodeType.prototype.configure = function () {
        this[VALUES] = arguments[0]?.widgets_values;
        return configure?.apply(this, arguments);
    };

    const onConfigure = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function () {
        onConfigure?.apply(this, arguments);
        const widgets_values = this[VALUES] || this.widgets_values;
        if (widgets_values?.length) {
            requestAnimationFrame(() => {
                populate.call(this, widgets_values, "onConfigure");
            });
        }
    };
}

app.registerExtension({
    name: "nce.utils.logic",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (!nodeData?.category?.startsWith("🐍 NCE")) return;
        console.log(nodeData.name);
        switch (nodeData?.name) {
            case "NCEShowAnything":
                NCEShowAnythingNodeCreated(nodeType, nodeData);
                break;
        }
    },
});
