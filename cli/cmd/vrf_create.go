package cmd

import (
	"errors"
	"fmt"

	"subnetter/internal/client"

	"github.com/spf13/cobra"
)

var vrfTenantID, vrfName, vrfRD string

var vrfCreateCmd = &cobra.Command{
	Use:   "create-vrf",
	Short: "Create a VRF",
	RunE: func(cmd *cobra.Command, args []string) error {
		if vrfTenantID == "" || vrfName == "" {
			return errors.New("--tenant-id and --name are required")
		}
		c := client.New(baseURL, idemKey)
		var rdPtr *string
		if vrfRD != "" {
			rdPtr = &vrfRD
		}
		v, err := c.CreateVRF(vrfTenantID, vrfName, rdPtr)
		if err != nil {
			return err
		}
		fmt.Printf("VRF created: %s  id=%s  tenant=%s  rd=%v\n", v.Name, v.ID, v.TenantID, v.RD)
		return nil
	},
}

func init() {
	rootCmd.AddCommand(vrfCreateCmd)
	vrfCreateCmd.Flags().StringVar(&vrfTenantID, "tenant-id", "", "tenant UUID (required)")
	vrfCreateCmd.Flags().StringVar(&vrfName, "name", "", "vrf name (required)")
	vrfCreateCmd.Flags().StringVar(&vrfRD, "rd", "", "route distinguisher (optional, e.g. 65000:1)")
}
