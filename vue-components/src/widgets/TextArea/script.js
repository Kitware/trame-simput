export default {
  name: 'swTextArea',
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
    'auto-grow': {
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
    'no-resize': {
      type: Boolean,
      default: false,
    },
    'row-height': {
      type: Boolean,
      default: false,
    },
    rows: {
      type: [String, Number],
      default: 5,
    },
  },
  data() {
    return {
      showHelp: false,
    };
  },
  computed: {
    model: {
      get() {
        /* eslint-disable no-unused-expressions */
        this.mtime; // force refresh
        return (this.properties() && this.properties()[this.name]) || '';
      },
      set(v) {
        this.properties()[this.name] = v;
      },
    },
    decorator() {
      /* eslint-disable no-unused-expressions */
      this.mtime; // force refresh
      return (
        this.domains()[this.name]?.decorator?.available || {
          show: true,
          enable: true,
        }
      );
    },
  },
  methods: {
    validate() {
      this.dirty(this.name);
    },
  },
  inject: ['data', 'properties', 'domains', 'dirty'],
};
