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
  name: "swSlider",
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
    layout: {
      type: String,
    },
    sizeControl: {
      type: Boolean,
      default: false,
    },
    min: {
      type: Number,
    },
    max: {
      type: Number,
    },
    step: {
      type: Number,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    readonly: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const simputChannel = inject("simputChannel");
    const data = inject("data");
    const properties = inject("properties");
    const domains = inject("domains");
    const dirty = inject("dirty");

    const showHelp = ref(false);
    const dynamicSize = ref(props.size);
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
        props.dynamicSize;
        return properties() && properties()[props.name];
      },
      set(v) {
        properties()[props.name] = v;
      },
    });

    const computedLayout = computed(() => {
      /* eslint-disable no-unused-expressions */
      props.mtime; // force refresh
      return props.layout || domains()[props.name]?.UI?.layout || "vertical";
    });

    const computedSize = computed(() => {
      if (Number(props.size.value) !== 1) {
        return Math.max(props.size, model.value.length);
      }
      return Number(props.size);
    });

    const computedSizeControl = computed(() => {
      /* eslint-disable no-unused-expressions */
      props.mtime; // force refresh
      return props.sizeControl || domains()[props.name]?.UI?.sizeControl;
    });

    const computedMin = computed(() => {
      if (props.min != null) {
        return props.min;
      }

      const dataRange =
        domains()?.[props.name]?.Range?.available ||
        domains()?.[props.name]?.range?.available;
      if (dataRange) {
        return dataRange[0];
      }
      return 0;
    });

    const computedMax = computed(() => {
      if (props.max != null) {
        return props.max;
      }

      const dataRange =
        domains()?.[props.name]?.Range?.available ||
        domains()?.[props.name]?.range?.available;
      if (dataRange) {
        return dataRange[1];
      }

      return 100;
    });

    const computedStep = computed(() => {
      if (props.step) {
        return props.step;
      }

      if (props.type.includes("int")) {
        return 1;
      }
      return 0.01;
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
      if (Number(props.size) !== 1) {
        model.value[component - 1] = convert.value(value);
        if (model.value[component - 1] === null) {
          model.value[component - 1] = props.initial[component - 1];
        }
        model.value = model.value.slice();
      } else {
        model.value !== convert.value(value);
        model.value = convert.value(value);
        if (model.value === null) {
          model.value = props.initial;
        }
      }
      dirty(props.name);
    };
    const addEntry = function addEntry() {
      props.dynamicSize = model.value.length + 1;
      model.value.length = props.dynamicSize;
      validate(dynamicSize.value);
    };

    const deleteEntry = function deleteEntry(index) {
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

    const update = function update(component = 0) {
      const value = component ? model.value[component - 1] : model.value;
      // must test against bool since it can be a string in case of error
      if (rule.value(value) === true) {
        if (Number(this.size) !== 1) {
          model.value[component - 1] = convert.value(value);
        } else {
          model.value = convert.value(value);
        }
        dirty(props.name);
      }
    };

    return {
      getComponentProps,
      validate,
      addEntry,
      deleteEntry,
      levelToIcon,
      levelToType,
      computedMin,
      computedMax,
      computedStep,
      computedSize,
      computedSizeControl,
      showHelp,
      data,
      decorator,
      rule,
      hints,
      shouldShow,
      model,
    };
  },
};
