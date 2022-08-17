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
      if (id && this.proxyId == id) {
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
        this.data = this.getSimput().getData(this.proxyId, true);
      }
      if (name === 'ui') {
        this.ui = this.getSimput().getUI(this.proxyId, true);
      }
      if (name === 'domain') {
        this.domains = this.getSimput().getDomains(this.proxyId, true);
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
    //   console.log(`~~~~ UI(${this.proxyId})`);
    // },
    // noUi() {
    //   console.log(`~~~~ noUI(${this.proxyId})`);
    // },
    // available() {
    //   console.log(`~~~~ available(${this.proxyId})`);
    // },
  },
  computed: {
    proxyId() {
      return `${this.itemId}`;
    },
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
        id: this.proxyId,
        data,
        domains,
        properties,
      };
    },
  },
  methods: {
    update() {
      if (this.proxyId) {
        this.data = this.getSimput().getData(this.proxyId);
        this.domains = this.getSimput().getDomains(this.proxyId);
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
