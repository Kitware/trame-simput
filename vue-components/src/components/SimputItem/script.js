import VRuntimeTemplate from 'v-runtime-template';

export default {
  name: 'SimputItem',
  props: {
    itemId: {
      type: String,
    },
    noUi: {
      type: Boolean,
      default: false,
    },
  },
  components: {
    VRuntimeTemplate,
  },
  data() {
    return {
      data: null,
      ui: null,
      domains: null,
    };
  },
  created() {
    this.onConnect = () => {
      this.update();
    };
    this.onChange = ({ id, type }) => {
      /* eslint-disable eqeqeq */
      if (id && this.itemId == id) {
        this.data = this.getSimput().getData(id);
        this.domains = this.getSimput().getDomains(id);
      }
      if (type && this.type === type) {
        this.ui = this.getSimput().getUI(this.type);
      }
      if (!type && this.type && !this.ui) {
        this.ui = this.getSimput().getUI(this.type);
      }
    };
    this.onReload = (name) => {
      if (name === 'data') {
        this.data = this.getSimput().getData(this.itemId, true);
      }
      if (name === 'ui') {
        this.ui = this.getSimput().getUI(this.itemId, true);
      }
      if (name === 'domain') {
        this.domains = this.getSimput().getDomains(this.itemId, true);
      }
    };
    this.simputChannel.$on('connect', this.onConnect);
    this.simputChannel.$on('change', this.onChange);
    this.simputChannel.$on('reload', this.onReload);
    this.update();
  },
  beforeDestroy() {
    this.simputChannel.$off('connect', this.onConnect);
    this.simputChannel.$off('change', this.onChange);
    this.simputChannel.$off('reload', this.onReload);
  },
  watch: {
    itemId() {
      // Clear previous data if its a different proxy
      this.data = null;
      this.ui = null;

      // Update data to match given itemId
      this.update();
    },
    // ui() {
    //   console.log(`~~~~ UI(${this.itemId})`);
    // },
    // noUi() {
    //   console.log(`~~~~ noUI(${this.itemId})`);
    // },
    // available() {
    //   console.log(`~~~~ available(${this.itemId})`);
    // },
  },
  computed: {
    type() {
      return this.data && this.data.type;
    },
    available() {
      return !!(this.data && this.domains && this.ui);
    },
    properties() {
      return this.data?.properties;
    },
    all() {
      const { data, domains, properties } = this;
      return {
        id: this.itemId,
        data,
        domains,
        properties,
      };
    },
  },
  methods: {
    update() {
      if (this.itemId) {
        this.data = this.getSimput().getData(this.itemId);
        this.domains = this.getSimput().getDomains(this.itemId);
        if (this.type) {
          this.ui = this.getSimput().getUI(this.type);
        }
        this.simputChannel.pushQuery();
      } else {
        this.data = null;
        this.ui = null;
      }
    },
    dirty(name) {
      this.simputChannel.$emit('dirty', { id: this.data.id, name });
    },
    dirtyMany(names) {
      this.simputChannel.$emit('dirty', { id: this.data.id, names });
    },
  },
  inject: ['simputChannel', 'getSimput'],
  provide() {
    return {
      // simputChannel: this.simputChannel,
      dirty: (name) => this.dirty(name),
      dirtyMany: (...names) => this.dirtyMany(names),
      data: () => this.data,
      domains: () => this.domains,
      properties: () => this.properties,
      uiTS: () => this.getSimput().getUITimeStamp(),
    };
  },
};
