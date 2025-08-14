import {
  useQuery,
  useDecorator,
  useConvert,
  useRule,
  useHints,
} from "../../core/utils";
const { ref, computed, onMounted, onBeforeUnmount, inject, toRef } = window.Vue;

// Layouts: horizontal, vertical, l2, l3, l4
export default {
  name: "swTextField",
  props: {
    name: {
      type: String,
    },
    size: {
      type: Number,
      default: 1,
    },
    label: {
      type: String,
    },
    help: {
      type: String,
    },
    mtime: {
      type: Number,
    },
    type: {
      type: String,
    },
    initial: {},
    // --- custom to current widget ---
    editColor: {
      type: String,
      default: "transparent",
    },
    layout: {
      type: String,
    },
    sizeControl: {
      type: Boolean,
      default: false,
    },
    allowRefresh: {
      type: Boolean,
      default: false,
    },
    newValue: {
      type: String,
      default: "same",
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    readonly: {
      type: Boolean,
      default: false,
    },
    proxyType: {
      type: String,
    },
  },
  setup(props) {
    const domains = inject("domains");
    const showHelp = ref(false);
    const dynamicSize = ref(props.size.value);
    const query = ref("");

    const { decorator } = useDecorator({
      domains,
      mtime: toRef(props.mtime),
      name: toRef(props.name),
    });

    const { shouldShow, textToQuery } = useQuery({
      query,
      label: toRef(props.label),
      name: toRef(props.name),
      decorator,
    });

    const { convert } = useConvert({ type: toRef(props.type) });

    const { rule } = useRule({ type: toRef(props.type) });

    const { hints } = useHints({
      domains,
      mtime: toRef(props.mtime),
      name: toRef(props.name),
    });

    const simputChannel = inject("simputChannel");
    const properties = inject("properties");
    const data = inject("data");
    const getSimput = inject("getSimput");
    const dirty = inject("dirty");

    const onQuery = function onQuery(query) {
      query.value = query;
    };

    onMounted(() => {
      simputChannel.$on("query", onQuery);
    });

    onBeforeUnmount(() => {
      simputChannel.$off("query", onQuery);
    });

    const model = computed({
      get() {
        /* eslint-disable no-unused-expressions */
        props.mtime; // force refresh
        dynamicSize.value;
        const value = properties() && properties()[props.name];
        if (!value && props.size > 1) {
          const emptyArray = [];
          emptyArray.length = props.size;
          return emptyArray;
        }
        return value;
      },
      set(v) {
        properties()[props.name] = v;
      },
    });

    const computedLayout = computed(() => {
      /* eslint-disable no-unused-expressions */
      props.mtime; // force refresh
      return props.layout || domains()[props.name]?.UI?.layout || "horizontal";
    });

    const computedSize = computed(() => {
      if (Number(props.size) !== 1) {
        return Math.max(props.size || 1, model.value?.length || 0);
      }
      return Number(props.size);
    });

    const computedSizeControl = computed(() => {
      /* eslint-disable no-unused-expressions */
      props.mtime; // force refresh
      return props.sizeControl || domains()[props.name]?.UI?.sizeControl;
    });

    const levelToType = function levelToType(level) {
      switch (level) {
        case 0:
          return "info";
        case 1:
          return "warning";
        case 2:
          return "error";
        default:
          return "success";
      }
    };

    const levelToIcon = function levelToIcon(level) {
      switch (level) {
        case 0:
          return "mdi-information-outline";
        case 1:
          return "mdi-alert-octagon-outline";
        case 2:
          return "mdi-alert-outline";
        default:
          return "mdi-brain";
      }
    };

    const validate = function validate(component = 0) {
      const value = component ? model.value[component - 1] : model.value;
      const newValue = convert.value(value);
      if (Number(props.size) !== 1) {
        model.value[component - 1] = newValue;
        if (newValue === null) {
          model.value[component - 1] = props.initial?.[component - 1];
        }
        model.value = model.value.slice();
      } else {
        model.value = newValue;
        if (model.value === null) {
          model.value = props.initial;
        }
      }
      dirty(props.name);
    };

    const refresh = function refresh() {
      getSimput().refresh(data().id, props.name);
    };

    const addEntry = function addEntry() {
      if (!model.value) {
        model.value = [];
      }

      if (props.type == "proxy") {
        getSimput()
          .wsClient.getConnection()
          .getSession()
          .call("simput.create_proxy", [
            simputChannel.managerId.value,
            props.proxyType,
          ])
          .then((proxy_id) => {
            if (proxy_id != undefined) {
              model.value.push(proxy_id);
              dirty(props.name);
            }
            dynamicSize.value = model.value.length;
            validate(dynamicSize.value);
          });
      } else {
        if (props.newValue === "null") {
          model.value.push(null);
        } else if (props.newValue === "same") {
          model.value.push(model.value[model.value.length - 2]);
        }
        dynamicSize.value = model.value.length;
        validate(dynamicSize.value);
      }
    };

    const deleteEntry = function deletEntry(index) {
      model.value.splice(index, 1);
      dirty(props.name);
    };

    const getComponentProps = function getComponentProps(index) {
      if (computedLayout.value === "vertical") {
        return { cols: 12 };
      }
      if (computedLayout.value === "l2") {
        return { cols: 6 };
      }
      if (computedLayout.value === "l3") {
        return { cols: 4 };
      }
      if (computedLayout.value === "l4") {
        return { cols: 3 };
      }
      if (computedLayout.value === "m3-half") {
        const attrs = { cols: 4 };
        if (index === 3) {
          attrs.offset = 4;
        }
        if (index === 5) {
          attrs.offset = 8;
        }
        return attrs;
      }
      return {};
    };

    const color = function color(component = 0) {
      if (
        component &&
        model.value?.[component - 1] !== props.initial?.[component - 1]
      ) {
        return props.editColor;
      }
      if (!component && model.value !== props.initial) {
        return props.editColor;
      }
      return undefined;
    };

    const update = function update(component = 0) {
      const value = component ? model.value[component - 1] : model.value;
      // must test against bool since it can be a string in case of error
      if (rule.value(value) === true) {
        if (Number(props.size) !== 1) {
          model.value[component - 1] = convert.value(value);
        } else {
          model.value = convert.value(value);
        }
        dirty(props.name);
      }
    };

    return {
      showHelp,
      computedSize,
      getComponentProps,
      validate,
      update,
      data,
      color,
      levelToType,
      levelToIcon,
      computedSizeControl,
      addEntry,
      deleteEntry,
      hints,
      rule,
      refresh,
      shouldShow,
      decorator,
      model,
    };
  },
};
