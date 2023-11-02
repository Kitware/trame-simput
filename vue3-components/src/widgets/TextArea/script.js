const { ref, computed, inject } = window.Vue;

export default {
  name: "swTextArea",
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
    // --- text-area-props ---
    "auto-grow": {
      type: Boolean,
      default: false,
    },
    autofocus: {
      type: Boolean,
      default: false,
    },
    clearable: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    readonly: {
      type: Boolean,
      default: false,
    },
    "no-resize": {
      type: Boolean,
      default: false,
    },
    "row-height": {
      type: Boolean,
      default: false,
    },
    rows: {
      type: [String, Number],
      default: 5,
    },
  },
  setup(props) {
    const showHelp = ref(false);
    const properties = inject("properties");
    const domains = inject("domains");
    const dirty = inject("dirty");

    const model = computed({
      get() {
        /* eslint-disable no-unused-expressions */
        props.mtime; // force refresh
        return (properties() && properties()[props.name]) || "";
      },
      set(v) {
        properties()[props.name] = v;
      },
    });

    const decorator = computed(() => {
      /* eslint-disable no-unused-expressions */
      props.mtime; // force refresh
      return (
        domains()[props.name]?.decorator?.available || {
          show: true,
          enable: true,
        }
      );
    });
    const validate = function validate() {
      dirty(props.name);
    };

    return {
      validate,
      decorator,
      model,
    };
  },
};
