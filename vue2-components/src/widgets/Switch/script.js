import { COMPUTED } from '../../core/utils';

export default {
  name: 'swSwitch',
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
    disabled: {
      type: Boolean,
      default: false,
    },
    readonly: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      showHelp: false,
      query: '',
    };
  },
  created() {
    this.onQuery = (query) => {
      this.query = query;
    };
    this.simputChannel.$on('query', this.onQuery);
  },
  beforeDestroy() {
    this.simputChannel.$off('query', this.onQuery);
  },
  computed: {
    ...COMPUTED.query,
    ...COMPUTED.decorator,
    ...COMPUTED.convert,
    model: {
      get() {
        /* eslint-disable no-unused-expressions */
        this.mtime; // force refresh
        return this.properties() && this.properties()[this.name];
      },
      set(v) {
        this.properties()[this.name] = v;
      },
    },
  },
  methods: {
    validate() {
      this.model = this.convert(this.model);
      this.dirty(this.name);
    },
  },
  inject: ['simputChannel', 'data', 'properties', 'domains', 'dirty'],
};
