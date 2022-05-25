export default {
  name: 'swHide',
  props: {
    property: {
      type: String,
    },
    domain: {
      type: String,
    },
    mtime: {
      type: Number,
    },
  },
  computed: {
    visible() {
      this.mtime; // eslint-disable-line
      const domain = this.domains()?.[this.property]?.[this.domain];
      if (!domain) {
        // no domain == valid
        return false;
      }
      return !domain.value;
    },
  },
  inject: ['properties', 'domains'],
};
