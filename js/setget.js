const { app } = window.comfyAPI.app;

// 基于 KJNodes 的 SetGet 实现,简化并适配 NCE Utils

// 根据类型设置颜色
function setColorAndBgColor(type) {
    const colorMap = {
        "DEFAULT": LGraphCanvas.node_colors.gray,
        "MODEL": LGraphCanvas.node_colors.blue,
        "LATENT": LGraphCanvas.node_colors.purple,
        "VAE": LGraphCanvas.node_colors.red,
        "CONDITIONING": LGraphCanvas.node_colors.brown,
        "IMAGE": LGraphCanvas.node_colors.pale_blue,
        "CLIP": LGraphCanvas.node_colors.yellow,
        "FLOAT": LGraphCanvas.node_colors.green,
        "MASK": { color: "#1c5715", bgcolor: "#1f401b" },
        "INT": { color: "#1b4669", bgcolor: "#29699c" },
        "CONTROL_NET": { color: "#156653", bgcolor: "#1c453b" },
        "STRING": { color: "#4a3b5c", bgcolor: "#6b5b7f" }, // NCE 紫色主题
    };

    const colors = colorMap[type] || colorMap["DEFAULT"];
    this.color = colors.color;
    this.bgcolor = colors.bgcolor;
}

function showAlert(message) {
    app.extensionManager.toast.add({
        severity: 'warn',
        summary: "NCE Set/Get",
        detail: `${message}`,
        life: 5000,
    });
}

const LGraphNode = LiteGraph.LGraphNode;

// NCESetNode - 设置节点
app.registerExtension({
    name: "NCESetNode",
    registerCustomNodes() {
        class NCESetNode extends LGraphNode {
            defaultVisibility = true;
            serialize_widgets = true;
            drawConnection = false;
            currentGetters = null;
            slotColor = "#FFF";
            canvas = app.canvas;
            menuEntry = "Show connections";

            constructor(title) {
                super(title);
                if (!this.properties) {
                    this.properties = {
                        "previousName": ""
                    };
                }
                this.properties.showOutputText = NCESetNode.defaultVisibility;

                const node = this;

                this.addWidget(
                    "text",
                    "Constant",
                    '',
                    (s, t, u, v, x) => {
                        node.validateName(node.graph);
                        if (this.widgets[0].value !== '') {
                            this.title = "NCESet_" + this.widgets[0].value;
                        }
                        this.update();
                        this.properties.previousName = this.widgets[0].value;
                    },
                    {}
                );

                this.addInput("*", "*");
                this.addOutput("*", '*');

                this.onConnectionsChange = function (
                    slotType,
                    slot,
                    isChangeConnect,
                    link_info,
                    output
                ) {
                    // 断开连接
                    if (slotType == 1 && !isChangeConnect) {
                        if (this.inputs[slot].name === '') {
                            this.inputs[slot].type = '*';
                            this.inputs[slot].name = '*';
                            this.title = "NCESet";
                        }
                    }
                    if (slotType == 2 && !isChangeConnect) {
                        if (this.outputs && this.outputs[slot]) {
                            this.outputs[slot].type = '*';
                            this.outputs[slot].name = '*';
                        }
                    }

                    // 连接
                    if (link_info && node.graph && slotType == 1 && isChangeConnect) {
                        const resolve = link_info.resolve(node.graph);
                        const type = (resolve?.subgraphInput ?? resolve?.output)?.type;
                        if (type) {
                            if (this.title === "NCESet") {
                                this.title = "NCESet_" + type;
                            }
                            if (this.widgets[0].value === '*') {
                                this.widgets[0].value = type;
                            }

                            this.validateName(node.graph);
                            this.inputs[0].type = type;
                            this.inputs[0].name = type;

                            setColorAndBgColor.call(this, type);
                        } else {
                            showAlert("node input undefined.");
                        }
                    }
                    if (link_info && node.graph && slotType == 2 && isChangeConnect) {
                        const fromNode = node.graph._nodes.find((otherNode) => otherNode.id == link_info.origin_id);

                        if (fromNode && fromNode.inputs && fromNode.inputs[link_info.origin_slot]) {
                            const type = fromNode.inputs[link_info.origin_slot].type;

                            this.outputs[0].type = type;
                            this.outputs[0].name = type;
                        } else {
                            showAlert('node output undefined');
                        }
                    }

                    this.update();
                };

                this.validateName = function (graph) {
                    let widgetValue = node.widgets[0].value;

                    if (widgetValue !== '') {
                        let tries = 0;
                        const existingValues = new Set();

                        graph._nodes.forEach(otherNode => {
                            if (otherNode !== this && otherNode.type === 'NCESetNode') {
                                existingValues.add(otherNode.widgets[0].value);
                            }
                        });

                        while (existingValues.has(widgetValue)) {
                            widgetValue = node.widgets[0].value + "_" + tries;
                            tries++;
                        }

                        node.widgets[0].value = widgetValue;
                        this.update();
                    }
                };

                this.clone = function () {
                    const cloned = NCESetNode.prototype.clone.apply(this);
                    cloned.inputs[0].name = '*';
                    cloned.inputs[0].type = '*';
                    cloned.value = '';
                    cloned.properties.previousName = '';
                    cloned.size = cloned.computeSize();
                    return cloned;
                };

                this.onAdded = function (graph) {
                    this.validateName(graph);
                };

                this.update = function () {
                    if (!node.graph) {
                        return;
                    }

                    const getters = this.findGetters(node.graph);
                    getters.forEach(getter => {
                        getter.setType(this.inputs[0].type);
                    });

                    if (this.widgets[0].value) {
                        const gettersWithPreviousName = this.findGetters(node.graph, true);
                        gettersWithPreviousName.forEach(getter => {
                            getter.setName(this.widgets[0].value);
                        });
                    }

                    const allGetters = node.graph._nodes.filter(otherNode => otherNode.type === "NCEGetNode");
                    allGetters.forEach(otherNode => {
                        if (otherNode.setComboValues) {
                            otherNode.setComboValues();
                        }
                    });
                };

                this.findGetters = function (graph, checkForPreviousName) {
                    const name = checkForPreviousName ? this.properties.previousName : this.widgets[0].value;
                    return graph._nodes.filter(otherNode => otherNode.type === 'NCEGetNode' && otherNode.widgets[0].value === name && name !== '');
                };

                // 纯前端节点,不序列化
                this.isVirtualNode = true;
            }

            onRemoved() {
                const allGetters = this.graph._nodes.filter((otherNode) => otherNode.type == "NCEGetNode");
                allGetters.forEach((otherNode) => {
                    if (otherNode.setComboValues) {
                        otherNode.setComboValues([this]);
                    }
                });
            }

            getExtraMenuOptions(_, options) {
                this.menuEntry = this.drawConnection ? "Hide connections" : "Show connections";
                options.unshift(
                    {
                        content: this.menuEntry,
                        callback: () => {
                            this.currentGetters = this.findGetters(this.graph);
                            if (this.currentGetters.length == 0) return;
                            let linkType = (this.currentGetters[0].outputs[0].type);
                            this.slotColor = this.canvas.default_connection_color_byType[linkType];
                            this.menuEntry = this.drawConnection ? "Hide connections" : "Show connections";
                            this.drawConnection = !this.drawConnection;
                            this.canvas.setDirty(true, true);
                        },
                    },
                    {
                        content: "Hide all connections",
                        callback: () => {
                            const allGetters = this.graph._nodes.filter(otherNode => otherNode.type === "NCEGetNode" || otherNode.type === "NCESetNode");
                            allGetters.forEach(otherNode => {
                                otherNode.drawConnection = false;
                            });

                            this.menuEntry = "Show connections";
                            this.drawConnection = false;
                            this.canvas.setDirty(true, true);
                        },
                    },
                );

                // 添加 Getters 子菜单
                this.currentGetters = this.findGetters(this.graph);
                if (this.currentGetters) {
                    let gettersSubmenu = this.currentGetters.map(getter => ({
                        content: `${getter.title} id: ${getter.id}`,
                        callback: () => {
                            this.canvas.centerOnNode(getter);
                            this.canvas.selectNode(getter, false);
                            this.canvas.setDirty(true, true);
                        },
                    }));

                    options.unshift({
                        content: "Getters",
                        has_submenu: true,
                        submenu: {
                            title: "GetNodes",
                            options: gettersSubmenu,
                        }
                    });
                }
            }

            onDrawForeground(ctx, lGraphCanvas) {
                if (this.drawConnection) {
                    this._drawVirtualLinks(lGraphCanvas, ctx);
                }
            }

            _drawVirtualLinks(lGraphCanvas, ctx) {
                if (!this.currentGetters?.length) return;

                const start_node_slotpos = this.flags.collapsed
                    ? [ctx.measureText(this.title).width + 55, -15]
                    : [this.size[0], LiteGraph.NODE_TITLE_HEIGHT * 0.5];

                const defaultLink = { type: 'default', color: this.slotColor };

                for (const getter of this.currentGetters) {
                    const end_node_slotpos = this.getConnectionPos(false, 0);
                    const offset = this.flags.collapsed
                        ? [getter.pos[0] - end_node_slotpos[0] + ctx.measureText(this.title).width + 50, getter.pos[1] - end_node_slotpos[1] - 30]
                        : [getter.pos[0] - end_node_slotpos[0] + this.size[0], getter.pos[1] - end_node_slotpos[1]];

                    lGraphCanvas.renderLink(
                        ctx,
                        start_node_slotpos,
                        offset,
                        defaultLink,
                        false,
                        null,
                        this.slotColor,
                        LiteGraph.RIGHT,
                        LiteGraph.LEFT
                    );
                }
            }
        }

        LiteGraph.registerNodeType(
            "NCESetNode",
            Object.assign(NCESetNode, {
                title: "NCESet",
            })
        );

        NCESetNode.category = "🐍 NCE/基础";
    },
});

// NCEGetNode - 获取节点
app.registerExtension({
    name: "NCEGetNode",
    registerCustomNodes() {
        class NCEGetNode extends LGraphNode {
            defaultVisibility = true;
            serialize_widgets = true;
            drawConnection = false;
            slotColor = "#FFF";
            currentSetter = null;
            canvas = app.canvas;

            constructor(title) {
                super(title);
                if (!this.properties) {
                    this.properties = {};
                }
                this.properties.showOutputText = NCEGetNode.defaultVisibility;
                const node = this;

                this.addWidget(
                    "combo",
                    "Constant",
                    "",
                    (e) => {
                        this.onRename();
                    },
                    {
                        values: () => {
                            const setterNodes = node.graph._nodes.filter((otherNode) => otherNode.type == 'NCESetNode');
                            return setterNodes.map((otherNode) => otherNode.widgets[0].value).sort();
                        }
                    }
                );

                this.addOutput("*", '*');

                this.onConnectionsChange = function (
                    slotType,
                    slot,
                    isChangeConnect,
                    link_info,
                    output
                ) {
                    this.validateLinks();
                };

                this.setName = function (name) {
                    node.widgets[0].value = name;
                    node.onRename();
                    node.serialize();
                };

                this.onRename = function () {
                    const setter = this.findSetter(node.graph);
                    if (setter) {
                        let linkType = (setter.inputs[0].type);

                        this.setType(linkType);
                        this.title = "NCEGet_" + setter.widgets[0].value;

                        setColorAndBgColor.call(this, linkType);
                    } else {
                        this.setType('*');
                    }
                };

                this.clone = function () {
                    const cloned = NCEGetNode.prototype.clone.apply(this);
                    cloned.size = cloned.computeSize();
                    return cloned;
                };

                this.validateLinks = function () {
                    if (this.outputs[0].type !== '*' && this.outputs[0].links) {
                        this.outputs[0].links.filter(linkId => {
                            const link = node.graph.links[linkId];
                            return link && (!link.type.split(",").includes(this.outputs[0].type) && link.type !== '*');
                        }).forEach(linkId => {
                            node.graph.removeLink(linkId);
                        });
                    }
                };

                this.setType = function (type) {
                    this.outputs[0].name = type;
                    this.outputs[0].type = type;
                    this.validateLinks();
                };

                this.findSetter = function (graph) {
                    const name = this.widgets[0].value;
                    const foundNode = graph._nodes.find(otherNode => otherNode.type === 'NCESetNode' && otherNode.widgets[0].value === name && name !== '');
                    return foundNode;
                };

                this.goToSetter = function () {
                    this.canvas.centerOnNode(this.currentSetter);
                    this.canvas.selectNode(this.currentSetter, false);
                };

                // 纯前端节点,不序列化
                this.isVirtualNode = true;
            }

            getInputLink(slot) {
                const setter = this.findSetter(this.graph);

                if (setter) {
                    const slotInfo = setter.inputs[slot];
                    const link = this.graph.links[slotInfo.link];
                    return link;
                } else {
                    const errorMessage = "No NCESetNode found for " + this.widgets[0].value + "(" + this.type + ")";
                    showAlert(errorMessage);
                }
            }

            onAdded(graph) {
            }

            getExtraMenuOptions(_, options) {
                let menuEntry = this.drawConnection ? "Hide connections" : "Show connections";
                this.currentSetter = this.findSetter(this.graph);
                if (!this.currentSetter) return;

                options.unshift(
                    {
                        content: "Go to setter",
                        callback: () => {
                            this.goToSetter();
                        },
                    },
                    {
                        content: menuEntry,
                        callback: () => {
                            let linkType = (this.currentSetter.inputs[0].type);
                            this.drawConnection = !this.drawConnection;
                            this.slotColor = this.canvas.default_connection_color_byType[linkType];
                            this.canvas.setDirty(true, true);
                        },
                    },
                );
            }

            onDrawForeground(ctx, lGraphCanvas) {
                if (this.drawConnection) {
                    this._drawVirtualLink(lGraphCanvas, ctx);
                }
            }

            _drawVirtualLink(lGraphCanvas, ctx) {
                if (!this.currentSetter) return;

                const defaultLink = { type: 'default', color: this.slotColor };

                let start_node_slotpos = this.currentSetter.getConnectionPos(false, 0);
                start_node_slotpos = [
                    start_node_slotpos[0] - this.pos[0],
                    start_node_slotpos[1] - this.pos[1],
                ];
                let end_node_slotpos = [0, -LiteGraph.NODE_TITLE_HEIGHT * 0.5];

                lGraphCanvas.renderLink(
                    ctx,
                    start_node_slotpos,
                    end_node_slotpos,
                    defaultLink,
                    false,
                    null,
                    this.slotColor
                );
            }
        }

        LiteGraph.registerNodeType(
            "NCEGetNode",
            Object.assign(NCEGetNode, {
                title: "NCEGet",
            })
        );

        NCEGetNode.category = "🐍 NCE/基础";
    },
});

// 保持 Set/Get 节点的虚拟连接在屏幕外时可见
app.registerExtension({
    name: "nce.utils.setget.visibility",
    async setup() {
        const originalComputeVisibleNodes = LGraphCanvas.prototype.computeVisibleNodes;
        LGraphCanvas.prototype.computeVisibleNodes = function () {
            const visibleNodesSet = new Set(originalComputeVisibleNodes.apply(this, arguments));
            for (const node of this.graph._nodes) {
                if ((node.type === "NCESetNode" || node.type === "NCEGetNode") && node.drawConnection) {
                    visibleNodesSet.add(node);
                }
            }
            return Array.from(visibleNodesSet);
        };
    }
});
