const { computed, inject } = window.Vue;

export default {
  name: "swShow",
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
  setup(props) {
    const properties = inject("properties");
    const domains = inject("domains");

    const isVisible = function isVisible() {
      this.mtime; // eslint-disable-line
      const domain = domains()?.[props.property]?.[props.domain];
      const propertyValue = properties()?.[props.property];
      if (!domain) {
        // no domain == valid
        return true;
      }
      return domain.available.map((v) => v.value).includes(propertyValue);
    };

    const visible = computed(isVisible);

    return {
      visible,
    };
  },
};
