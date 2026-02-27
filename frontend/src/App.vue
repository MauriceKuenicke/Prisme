<template>
  <router-view />
  <PwaInstallNotice />
</template>

<script setup>
import PwaInstallNotice from '@/components/PwaInstallNotice.vue'
</script>

<style>
@import './assets/styles/base.css';
@import './assets/styles/utilities.css';
</style>
